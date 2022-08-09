import logging
import logging.config
import random
import time

from transitions import EventData, Machine

logging.config.fileConfig(
    "logConfig.ini",
    disable_existing_loggers=False,
)
app_logger = logging.getLogger("app")
app_logger.info("Starting App")


class OrderEntryException(Exception):
    pass


class TradeBot(Machine):
    # Set bot parameters on the class.
    # One class per bot with custom logic... 0dte, WO, 112's, Strangles, Theta Enginer
    target_delta = 0.05
    target_dte = 30
    failed_to_fill_order = True
    close_for_pt = False
    close_for_sl = False

    def open_position(self, event: EventData):
        print(self.state)
        print("Opening a Position")
        time.sleep(1)  # Simulate the work
        # Loop on some interval to find an entry
        # Place the order
        # Persist the opening order details in our DB
        # Notifications in Telegram/Discord

    def monitor_position(self, event: EventData):
        print(self.state)
        print("Monitoring a Position")
        time.sleep(1)  # Simulate the work
        # Loop to monitor the trade and look for an exit condition, PT or Stop Loss, before closing
        var = random.random()
        if var < 0.5:
            self.close_for_pt = True
        else:
            self.close_for_sl = True

    def close_position_for_pt(self, event: EventData):
        print("Attempting to close the Position for a Profit")
        time.sleep(1)  # Simulate the work
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
        time.sleep(1)  # Simulate the work
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
        time.sleep(1)  # Simulate the work
        # Final logging to discord, telegram alerts, db records?

    def handle_error(self, event: EventData):
        # Reprocess Order Entry Exceptions
        if type(event.error) == type(OrderEntryException()):
            source_name = event.transition.source
            print(
                f"Error occurred. Transitioned from State {source_name}. Will transition back."
            )
            self.close_for_pt = False
            self.close_for_sl = False
            self.trigger(f"to_{source_name}")
        # Handle other exception types differently
        # Send Notifications

    def save(self, event: EventData):
        print(f"Saving {self.state} state.")
        # Persist the bot as a pickled object in our DB in case we need to restore it.
        time.sleep(0.5)  # Simulate the work

    def run(self):
        # Run forever until we are closed.
        while self.state != "Closed":
            # Got the possible triggers for our state
            a = self.get_triggers(self.state)

            # Loop and try each, ignoring the default "to_" triggers
            triggers = [x for x in a if not x.startswith("to_")]
            for trig in triggers:
                if self.trigger(trig):
                    break

    def __init__(self):
        # Define our states, saving the bot status when we enter the states.
        states = [
            {"name": "Initial"},
            {"name": "Open", "on_enter": ["save", "monitor_position"]},
            {"name": "Closed", "on_enter": ["save", "cleanup_position"]},
        ]

        transitions = [
            {
                "trigger": "OpenPosition",
                "source": "Initial",
                "dest": "Open",
                "before": "open_position",
            },
            {
                "trigger": "ClosePositionAtPT",
                "source": "Open",
                "dest": "Closed",
                "before": "close_position_for_pt",
                "conditions": "close_for_pt",
            },
            {
                "trigger": "",
                "source": "Open",
                "dest": "Closed",
                "before": "close_position_for_sl",
                "conditions": "close_for_sl",
            },
        ]

        # init the machine with our states, starting at 'Initial', handling errors, sending event data, generating default transitions, and ignoring invalid triggers
        Machine.__init__(
            self,
            states=states,
            transitions=transitions,
            initial="Initial",
            on_exception="handle_error",
            send_event=True,
            auto_transitions=True,
            ignore_invalid_triggers=True,
        )


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
