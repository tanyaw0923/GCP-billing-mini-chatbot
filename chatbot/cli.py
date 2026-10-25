from chatbot import CreditChatbot

if __name__ == '__main__':
    chatbot = CreditChatbot()
    print('GCP Credit Tracker. Type exit to quit.')
    while True:
        question = input('\nYou: ').strip()
        if question.lower() in ('exit', 'quit'):
            break
        if question:
            try:
                print('\n' + chatbot.ask(question))
            except Exception as exc:
                print(f'Query failed: {exc}')
