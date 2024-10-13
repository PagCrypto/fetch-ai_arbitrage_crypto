from uagents import Agent, Context, Model

agent = Agent()

agentSender = "agent1qvp58kzmem2nsc7r4kl5htt9hnvhsd9gxt6h4tzq5nv028hfrmrmsmnxev8"
agentConsumer = "agent1qw3ezrfth87498566uhe9jek7dhs73rcs7q0nc5rqdayn0l5xgn7z7pykg9"

class MessageRequest(Model):
    message: str

class OpportunitiesRequest(Model):
    opportunities = []

@agent.on_message(model=MessageRequest)
async def handle_message(ctx: Context, sender: str, msg: MessageRequest):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")

    if sender == agentSender:
        await ctx.send(sender, MessageRequest(message="hello sender, i received a message!"))
    else:
        await ctx.send(sender, MessageRequest(message="hello i received."))


@agent.on_message(model=OpportunitiesRequest)
async def handle_opportunities(ctx: Context, sender: str, msg: OpportunitiesRequest):
    ctx.logger.info(f"Received Opportunities from {sender}: {msg.opportunities}")
    
    if msg.opportunities:
        for opportunity in msg.opportunities:
            ctx.logger.info(opportunity)
            # Opcional: Executar trade automático, com base nas oportunidades
            # Exemplo: execute_binance_trade("BTCUSDT", "BUY", 0.001)
    else:
        ctx.logger.info("Nenhuma oportunidade de arbitragem foi encontrada.")

    ctx.storage.set("oportunities", msg.opportunities)
  
if __name__ == "__main__":
    agent.run()
    
