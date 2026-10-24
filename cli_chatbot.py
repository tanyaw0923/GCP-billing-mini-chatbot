#!/usr/bin/env python3

from chatbot import CostOptimizerChatbot
from bigquery_client import BigQueryClient
from tabulate import tabulate
from colorama import Fore, Style, init
import sys

init(autoreset=True)


class CLIChatbot:
    """Command-line chatbot interface."""

    def __init__(self):
        """Initialize CLI chatbot."""
        print(f"{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.CYAN} GCP Cost Optimization Chatbot")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\\n")

        print(f"{Fore.YELLOW} Initializing...{Style.RESET_ALL}")
        self.chatbot = CostOptimizerChatbot()
        self.bq_client = BigQueryClient()
        print(f"{Fore.GREEN} Ready!{Style.RESET_ALL}\\n")

    def show_dashboard(self):
        """Display dashboard."""
        print(f"\\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.CYAN} COST DASHBOARD")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\\n")

        total = self.bq_client.get_total_cost()
        projects = self.bq_client.get_project_breakdown()
        top = self.bq_client.get_top_cost_drivers(5)

        print(f"{Fore.GREEN} Total: ${total:,.2f}{Style.RESET_ALL}")
        print(f"{Fore.GREEN} Projects: {len(projects)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN} Services: {len(top)}{Style.RESET_ALL}\\n")

        if top:
            print(f"{Fore.YELLOW}Top Cost Drivers:{Style.RESET_ALL}\\n")
            table = [
                [i["service_description"], f"${float(i['total_cost']):,.2f}"]
                for i in top
            ]
            print(tabulate(table, headers=["Service", "Cost"], tablefmt="grid"))
            print()

    def process_query(self, query: str):
        """Process query."""
        print(f"\\n{Fore.CYAN}Query: {query}{Style.RESET_ALL}\\n")

        result = self.chatbot.process_query(query)

        if result["status"] == "success":
            meta = result["metadata"]
            print(f"{Fore.YELLOW}Summary:{Style.RESET_ALL}")
            print(f" Total: ${meta['total_cost']:,.2f}")
            print(f" Projects: {meta['total_projects']}")
            print(f" Services: {meta['total_services']}\\n")

            print(f"{Fore.GREEN}{'=' * 80}")
            print("AI ANALYSIS")
            print(f"{'=' * 80}{Style.RESET_ALL}\\n")
            print(result["analysis"])
        else:
            print(f"{Fore.RED}{result['message']}{Style.RESET_ALL}")

    def show_help(self):
        """Show help."""
        print(f"\\n{Fore.CYAN}COMMANDS:{Style.RESET_ALL}")
        print(" dashboard - Show cost dashboard")
        print(" help - Show this help")
        print(" quit/exit - Exit chatbot")

        print(f"\\n{Fore.YELLOW}EXAMPLE QUERIES:{Style.RESET_ALL}")
        print(" What are my top cost drivers?")
        print(" How can I reduce Compute Engine costs?")
        print(" Compare production vs development")
        print()

    def run(self):
        """Run chatbot loop."""
        self.show_dashboard()
        self.show_help()

        while True:
            try:
                user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "q"]:
                    print(f"\\n{Fore.CYAN} Goodbye!{Style.RESET_ALL}\\n")
                    break

                elif user_input.lower() == "dashboard":
                    self.show_dashboard()

                elif user_input.lower() == "help":
                    self.show_help()

                else:
                    self.process_query(user_input)

            except KeyboardInterrupt:
                print(f"\\n\\n{Fore.CYAN} Goodbye!{Style.RESET_ALL}\\n")
                break
            except Exception as e:
                print(f"\\n{Fore.RED}Error: {e}{Style.RESET_ALL}\\n")


def main():
    """Main entry point."""
    try:
        cli = CLIChatbot()
        cli.run()
    except Exception as e:
        print(f"\\n Fatal error: {e}\\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
