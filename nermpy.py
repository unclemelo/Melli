import os
import nerimity.client
from colorama import Fore

# Initialize the Nerimity client
nerimity_client = nerimity.client.Client(
    token=os.getenv("NERIMITY_TOKEN"),  # Replace with your actual token or load it using environment variables
    prefix="!",
)

# Register a Nerimity command
@nerimity_client.command("hello")
async def hello_command(ctx: nerimity.client.Context, args: list[str]):
    """A Nerimity bot command to greet."""
    await ctx.respond(f"Hello, {args[0]}!")

def start_nerimity_client():
    """Starts the Nerimity client."""
    try:
        print(f"{Fore.YELLOW}Starting Nerimity client...{Fore.RESET}")
        nerimity_client.run(debug_mode=False)  # Start the blocking Nerimity client
    except SystemExit as e:
        print(f"{Fore.RED}[ ERROR ] Nerimity client exited: {e}{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}[ ERROR ] Failed to start Nerimity client: {e}{Fore.RESET}")

if __name__ == "__main__":
    start_nerimity_client()
