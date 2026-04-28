"""Entry point for the Convert graph.

Overview:
    * Extends :class:`BaseGraph` to build a LangGraph StateGraph.
    * Uses :class:`State` as the underlying state container.
    * Pipeline: ImageValidateNode → (branch) → EmoticonGenerateNode → ImageFormatNode

Official document URL: 
    - Graph API: https://docs.langchain.com/oss/python/langgraph/graph-api
    - StateGraph: https://docs.langchain.com/oss/python/langgraph/graph-api#stategraph
"""

from langgraph.graph import END, START, StateGraph

from casts.base_graph import BaseGraph
from casts.convert.modules.conditions import validate_route
from casts.convert.modules.nodes import (
    EmoticonGenerateNode,
    ImageFormatNode,
    ImageValidateNode,
)
from casts.convert.modules.state import InputState, OutputState, State


class ConvertGraph(BaseGraph):
    """Graph definition for Convert.

    Attributes:
        input: Input schema for the graph.
        output: Output schema for the graph.
        state: State schema for the graph.
    """

    def __init__(self) -> None:
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        """Builds and compiles the Convert graph.

        Returns:
            CompiledStateGraph: Compiled graph ready for execution.
        """
        builder = StateGraph(
            self.state, input_schema=self.input, output_schema=self.output
        )

        builder.add_node("ImageValidateNode", ImageValidateNode())
        builder.add_node("EmoticonGenerateNode", EmoticonGenerateNode())
        builder.add_node("ImageFormatNode", ImageFormatNode())

        builder.add_edge(START, "ImageValidateNode")
        builder.add_conditional_edges(
            "ImageValidateNode",
            validate_route,
            {"EmoticonGenerateNode": "EmoticonGenerateNode", END: END},
        )
        builder.add_edge("EmoticonGenerateNode", "ImageFormatNode")
        builder.add_edge("ImageFormatNode", END)

        graph = builder.compile()
        graph.name = self.name
        return graph


convert_graph = ConvertGraph()


convert_graph = ConvertGraph()
