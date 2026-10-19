from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import classify_node,clarify_node,retrieve_node,call_api_node

graph=StateGraph(AgentState)
graph.add_node('classify',classify_node)
graph.add_node('retrieve',retrieve_node)
graph.add_node('call_api',call_api_node)
graph.add_node('clarify',clarify_node)


graph.set_entry_point('classify')
graph.add_conditional_edges('classify',
                            lambda state:state['route'],
                            {'retrieve':'retrieve','call_api':'call_api','clarify':'clarify'})
graph.add_edge('retrieve',END)
graph.add_edge('call_api',END)
graph.add_edge('clarify',END)

app=graph.compile()