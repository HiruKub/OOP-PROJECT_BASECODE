from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool
def add(string :str) :
    """found string"""
    print("tool add Found!!! : ")
    return {string : "apple"}

if __name__ == "__main__":
    mcp.run()