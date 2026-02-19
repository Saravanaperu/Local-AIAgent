import json
from google.ai.generativelanguage import Content, Part, FunctionResponse

def execute_agent_loop(
    get_response_fn,
    history,
    tool_executor,
    max_iterations=10,
    log_func=None
):
    """
    Executes the agent loop.

    Args:
        get_response_fn: A function that takes history as input and returns a response object.
        history: The conversation history list.
        tool_executor: A function that takes tool_name and tool_args, executes the tool, and returns the result string.
        max_iterations: Maximum number of iterations.
        log_func: Optional function for logging (e.g., print).
    """
    if log_func is None:
        log_func = lambda x: None

    for i in range(max_iterations):
        log_func(f"Iteration {i+1}/{max_iterations}")
        try:
            response = get_response_fn(history)
        except Exception as e:
            return f"Error calling agent: {e}"

        # Check for empty response
        if not response.parts:
             return "Error: Empty response from agent."

        part = response.parts[0]

        # Check for function call
        if hasattr(part, 'function_call') and part.function_call:
            fc = part.function_call
            tool_name = fc.name
            tool_args = dict(fc.args)

            log_func(f"Agent calls tool: {tool_name} with {tool_args}")

            # Append model's tool call to history
            # We assume response.candidates[0].content is the correct object to append
            history.append(response.candidates[0].content)

            # Execute tool
            try:
                result = tool_executor(tool_name, tool_args)
            except Exception as e:
                result = f"Error executing tool {tool_name}: {e}"

            log_func(f"Tool Result: {result[:200]}..." if len(str(result)) > 200 else f"Tool Result: {result}")

            # Append tool response to history
            # Create the Part with FunctionResponse
            func_response_part = Part(
                function_response=FunctionResponse(
                    name=tool_name,
                    response={"result": result}
                )
            )

            # Append as a Content object with role 'function'
            history.append(Content(role="function", parts=[func_response_part]))

        elif hasattr(part, 'text') and part.text:
            # Final answer
            history.append(response.candidates[0].content)
            return part.text
        else:
             # Fallback for text if part.text is missing but it's text
             try:
                text = response.text
                history.append(response.candidates[0].content)
                return text
             except:
                return "Error: Unexpected response format."

    return "Agent: Maximum iterations reached without final answer."
