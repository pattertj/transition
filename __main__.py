import random
import time
from transitions import Machine, State, EventData

class OrderEntryException(Exception):
    pass
    

class TradeBot(Machine):
    # Set bot parameters on the class.
    # One class per bot with custom logic... 0dte, WO, 112's, Strangles, Theta Enginer
    target_delta = .05
    target_dte = 30
    failed_to_fill_order = True
    close_for_pt = False
    close_for_sl = False
    
    def open_position(self, event: EventData):
        print(self.state)
        print("Opening a Position")
        time.sleep(1) # Simulate the work
        # Loop on some interval to find an entry
        # Place the order
        # Persist the opening order details in our DB
        # Notifications in Telegram/Discord
        
    def monitor_position(self, event: EventData): 
        print(self.state)
        print("Monitoring a Position")
        time.sleep(1) # Simulate the work
        # Loop to find an exit condition, PT or Stop Loss, before closing
        var = random.random()
        if var < .5:
            self.close_for_pt = True
        else:
            self.close_for_sl = True

    def close_position_for_pt(self, event: EventData): 
        print("Attempting to close the Position for a Profit")
        time.sleep(1) # Simulate the work
        # Place the closing Order
        
        # Perhaps after some condition, we throw an exception and go back to monitoring?
        if self.failed_to_fill_order:
            print("Failed to Close Position")
            self.failed_to_fill_order = False
            raise OrderEntryException("Error")
        
        print("Successful Close")
        # Persist the closing order details in our DB
        # Notifications in Telegram/Discord
        
    def close_position_for_sl(self, event: EventData): 
        print("Attempting to close the Position for a Stop Loss")
        time.sleep(1) # Simulate the work
        # Place the closing Order
        
        # Perhaps after some condition, we throw an exception and go back to monitoring?
        if self.failed_to_fill_order:
            print("Failed to Close Position")
            self.failed_to_fill_order = False
            raise OrderEntryException("Error")
        
        print("Successful Close")
        # Persist the closing order details in our DB
        # Notifications in Telegram/Discord
    
    def cleanup_position(self, event: EventData):
        print(self.state)
        print("Cleaning up a Position")
        time.sleep(1) # Simulate the work
        # Final logging to discord, telegram alerts, something else?
        
    def handle_error(self, event: EventData):
        # Reprocess Order Entry Exceptions
        if type(event.error) == type(OrderEntryException()):
            source_name = event.transition.source
            print(f"Error occurred. Transitioned from State {source_name}. Will transition back.")
            self.close_for_pt = False
            self.close_for_sl = False
            self.trigger(f'to_{source_name}')        
        # Notifications or Cleanup
        
    def save(self, event: EventData):
        print(f"Saving {self.state} state.")
        # persiste the bot as a pickled object in our DB
        time.sleep(.5) # Simulate the work

    def run(self):
        while self.state != 'Closed':
            # Got the possible triggers for our state
            a = self.get_triggers(self.state)
            
            # Loop and try each, ignoring the default "to_" triggers and "Error"
            triggers = [x for x in a if not x.startswith("to_")]
            for trig in triggers:
                if self.trigger(trig):
                    break

    def __init__(self):
        # Define our states, saving the bot status when we enter the states, opening and closing positions as we exit.
        states = [
            State('Initial'),
            State('Open', on_enter=['save', 'monitor_position']),
            State('Closed', on_enter=['save', 'cleanup_position']),
            ]
        
        # init the machine with our states, handling errors, starting at 'Initial', sending event data, not generating default transitions, and ignoring invalid triggers
        Machine.__init__(self, states=states, initial='Initial', on_exception='handle_error', send_event=True, auto_transitions=True, ignore_invalid_triggers=True)  # 
        
        # Simple transition sequence in this example, but could be more complex if the strategy required it.
        self.add_transition('OpenPosition', 'Initial', 'Open', before=['open_position'])
        self.add_transition('ClosePositionAtPT', 'Open', 'Closed', before=['close_position_for_pt'], conditions=['close_for_pt'])
        self.add_transition('ClosePositionAtSL', 'Open', 'Closed', before=['close_position_for_sl'], conditions=['close_for_sl'])

# Build and run our bot
if __name__ == "__main__":
    bot = TradeBot()
    bot.run()
    
### Concept ###
# Run the bot until the state is closed. the sequence of functions should be:
# STATE IS INITIAL >>> open_position >>> STATE IS OPEN >>> save >>> monitor_position >>> close_position >>> STATE IS CLOSED >>> save >>> cleanup_position

# If at any point there is an exception it is handled in 'handle_error'.
# Exceptions in 'open_position' and 'close_position', will stop the state change and attempt to rollback to the source state and start over.
# Exceptions in 'cleanup_position' and 'monitor_position' will continue processing the state and not rollback
    
### Output ###

# Initial
# Opening a Position
# Saving Open state.
# Open
# Monitoring a Position
# Attempting to close the Position for a Stop Loss
# Failed to Close Position
# Error occurred. Transitioned from State Open. Will transition back.
# Saving Open state.
# Open
# Monitoring a Position
# Attempting to close the Position for a Profit
# Successful Close
# Saving Closed state.
# Closed
# Cleaning up a Position