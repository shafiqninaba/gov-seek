"""
This script demonstrates a retrieval pipeline that uses a memory saver to store the sources of retrieved documents.
The pipeline retrieves information related to a query, generates a response using the retrieved content, and saves the sources of the retrieved documents in memory.
"""

from langgraph.graph import MessagesState, StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import END
from langgraph.prebuilt import tools_condition
from langchain.chat_models import init_chat_model
from langchain_qdrant import QdrantVectorStore
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from typing import List, TypedDict
from langchain_core.messages import AIMessage
from uuid import uuid4
from loguru import logger
import re

load_dotenv()


class ConfigSchema(TypedDict):
    """Config schema for the retrieval pipeline."""

    sources: List[str]


class RetrievalPipeline:
    def __init__(self):
        """Initialize the retrieval pipeline."""
        self.graph_builder = StateGraph(MessagesState, config_schema=ConfigSchema)
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = QdrantVectorStore.from_existing_collection(
            embedding=self.embeddings,
            collection_name="demo_collection",
            url=os.environ.get("QDRANT_URL"),
            api_key=os.environ.get("QDRANT_API_KEY"),
        )

        @tool(response_format="content_and_artifact")
        def retrieve(query: str):
            """Retrieve information related to a query."""
            retrieved_docs = self.vector_store.similarity_search(query, k=2)
            serialized = "\n\n".join(
                (f"Source: {doc.metadata['source']}\n" f"Content: {doc.page_content}")
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs

        self.retrieve_tool = retrieve

        # Step 1: Generate an AIMessage that may include a tool-call to be sent.
        def query_or_respond(state: MessagesState):
            """Generate tool call for retrieval or respond."""
            llm_with_tools = self.llm.bind_tools([self.retrieve_tool])
            response = llm_with_tools.invoke(state["messages"])
            # MessagesState appends messages to state instead of overwriting
            return {"messages": [response]}

        self.query_or_respond = query_or_respond

        # Step 2: Execute the retrieval.
        self.tools = ToolNode([self.retrieve_tool])

        # Step 3: Generate a response using the retrieved content.
        def generate(state: MessagesState):
            """Generate answer."""
            # Get generated ToolMessages
            recent_tool_messages = []
            for message in reversed(state["messages"]):
                if message.type == "tool":
                    recent_tool_messages.append(message)
                else:
                    break
            tool_messages = recent_tool_messages[::-1]

            # Format into prompt
            docs_content = "\n\n".join(doc.content for doc in tool_messages)

            # find the links in the content located in "Source: {doc.metadata['source']}\n"
            links = re.findall(r"(?<=Source: ).*?(?=\n)", docs_content)
            links = list(set(links))

            # remove the "Source: {doc.metadata['source']}\n" from the content
            docs_content = re.sub(r"Source: .*?\n", "", docs_content)

            system_message_content = (
                "You are GovSeek, an assistant for question-answering tasks."
                "Use the following pieces of retrieved context to answer "
                "the question. The context were retrieved from the links found in https://www.gov.sg/trusted-sites. "
                "If you don't know the answer, say that you "
                "don't know."
                "\n\n"
                f"{docs_content}"
            )
            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "system")
                or (message.type == "ai" and not message.tool_calls)
            ]
            prompt = [SystemMessage(system_message_content)] + conversation_messages

            # Run
            response = self.llm.invoke(prompt)

            # Create a new AIMessage with the updated content
            response_with_sources = AIMessage(
                content=response.content, additional_kwargs={"sources": links}
            )

            return {
                "messages": [response_with_sources],
            }

        self.generate = generate

        self.graph_builder.add_node(self.query_or_respond)
        self.graph_builder.add_node(self.tools)
        self.graph_builder.add_node(self.generate)

        self.graph_builder.set_entry_point("query_or_respond")
        self.graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        self.graph_builder.add_edge("tools", "generate")
        self.graph_builder.add_edge("generate", END)

        self.memory = MemorySaver()
        self.graph = self.graph_builder.compile(checkpointer=self.memory)

    def run(self, input_message: str, thread_id: str):
        """Run the retrieval pipeline with optional thread_id for continued conversations."""
        # Use provided thread_id or generate a new one
        config = {"configurable": {"thread_id": thread_id}}

        full_response = ""
        sources = []
        for step in self.graph.stream(
            {"messages": [{"role": "user", "content": input_message}]},
            stream_mode="values",
            config=config,
        ):
            if "messages" in step:
                message = step["messages"][-1]
                logger.info(message)
                if hasattr(message, "content"):
                    full_response = message.content
                if hasattr(message, "additional_kwargs"):
                    sources = message.additional_kwargs.get("sources", [])

        logger.info(f"Sources: {sources}")
        return full_response, sources

    def get_conversation_history(self, thread_id: str):
        """Retrieve previous conversation by thread_id."""
        if thread_id in self.memory.checkpoints:
            return self.memory.checkpoints[thread_id]
        return None


if __name__ == "__main__":
    # Example usage:
    thread_id = str(uuid4())
    pipeline = RetrievalPipeline()
    first_response, sources = pipeline.run("hi my name is shafiq", thread_id)
    logger.info(f"First response: {first_response}\nThread ID: {thread_id}")

    # Continue the conversation
    second_response, sources = pipeline.run("what is my name", thread_id)
    logger.info(f"Second response: {second_response}")
