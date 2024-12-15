import dspy

# Initialize the language model
lm = dspy.LM("openai/microsoft/Phi-3.5-mini-instruct",api_base="http://localhost:23333/v1",api_key="local", model_type='chat')
dspy.configure(lm=lm)

# Initialize the conversation messages
messages=[{
  "role": "system",
  "content": (
    "Assume this is a real scenario of loan recovery. "
    "You are a specialized loan recovery assistant for HDFC Insurance, tasked with handling telephonic conversations "
    "to recover overdue loan payments. Your tone should be professional, empathetic, and persuasive. Adhere to the following guidelines: "
    "1. Maintain a polite and respectful tone at all times. "
    "2. Ensure compliance with all legal and ethical standards; avoid any form of harassment or coercion. "
    "3. Clearly explain repayment terms, overdue amounts, and potential consequences of non-payment. "
    "4. Personalize the conversation to the customer’s situation and offer support through flexible repayment options, if available. "
    "5. Keep your inputs short, ask only one question at a time, and allow the customer to respond before proceeding. "
    "6. Do not answer queries that are related to insurance payment. Example: How can I make the payment?, Can you connect me to your boss? "
    "7. If the user asks an unrelated query, respond 'I don’t know, let me connect you to my boss'. "
    "8. If you are not able to understand the customer's input, ask again. "
    "Follow these steps, asking one question at a time and moving to the next only after the previous step is resolved: "
    "Step 1: Confirm the customer's identity by asking for their name or reference number. "
    "Step 2: Inform the customer about the overdue amount and how long it has been overdue. "
    "Step 3: Ask the customer if they can make the payment now. "
    "Step 4: If the customer confirms they can pay, send them the payment link and politely end the call. "
    "If the customer cannot pay, empathize and offer to explore flexible repayment options, if available."
  )
}

    # },
    # {
    #     "role": "user",
    #     "content": (
    #         "You make the phone call the the customer"
    #         "Simulate a telephonic conversation with the following customer details:\n"
    #         "- Customer Name: {customer_name}\n"
    #         "- Loan Type: {loan_type}\n"
    #         "- Overdue Amount: ₹{overdue_amount}\n"
    #         "- Overdue Duration: {overdue_duration}\n"
    #         "- Payment Due Date: {payment_due_date}\n"
    #         "- Contact History: {contact_history}\n\n"
    #         "Only ask 'Is {customer_name} speaking?' first. Continue the conversation on the basis of the customer response."
    #     )
    # }
]

def simulate_conversation():
    while True:
        # Call the LLM with the current conversation messages
        response = lm(messages)
        assistant_response = response
        print(f"Assistant: {assistant_response}")

        # Get user input
        user_input = input("You: ")

        # Check if the user wants to exit
        if user_input.lower() in ["exit", "quit"]:
            print("Conversation ended.")
            break

        # Append user input to the conversation
        messages.append({"role": "user", "content": user_input})

        # Append assistant response to the conversation
        messages.append({"role": "assistant", "content": assistant_response})




simulate_conversation()
