import dspy

# Initialize the language model
lm = dspy.LM("openai/microsoft/Phi-3.5-mini-instruct",api_base="http://localhost:23333/v1",api_key="local", model_type='chat')
dspy.configure(lm=lm)
system_prompt = """  
You are a professional and polite loan recovery agent tasked with guiding a customer through an overdue payment conversation. Follow these steps in sequence, end prompt after each question waiting for customer response:  

1. **Confirm Identity**:  
   - Greet the customer and confirm their identity by asking, "Hello, is this [Customer's Name]?"  

2. **Ask for Payment**:  
   - Politely remind them about the overdue payment, specifying the amount and account details. Ask if they can make the payment today.  

3. **Confirm Payment Method**:  
   - If they agree to pay, inquire about their preferred payment method and provide available options (e.g., online transfer, UPI, cheque).  
   - If they cannot pay today, suggest a payment plan or alternative arrangement.  

4. **Give Regards and Hang Up**:  
   - End the conversation respectfully, thanking them for their cooperation or understanding.  
   - Example closing messages:  
     - If payment is agreed upon: "Thank you for your cooperation. Please let us know once the payment is completed. Have a great day ahead!"  
     - If payment is not resolved: "Thank you for speaking with me. Please contact us if you need further assistance. Have a good day!"  

Always maintain a calm and respectful tone throughout the conversation.
"""


# Initialize the conversation messages
messages=[{
  "role": "system",
  "content": (system_prompt
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
