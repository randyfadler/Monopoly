import random
import json
import tkinter as tk
import datetime
from tkinter import messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

# =============================================================================
# GLOBAL CONSTANTS
# =============================================================================
SHORT_GAME = False
TURN_LIMIT = 140
RENT_MULTIPLIER = 2.0
WEALTH_TAX_RATE = 0.20

DEFAULT_GRID_SIZE = 40
CELL_SIZE = 50
MARGIN = 30

LOG_FILE = "monopoly_log.txt"


house_costs = {
    "Brown": 50,
    "Light Blue": 50,
    "Pink": 100,
    "Orange": 100,
    "Red": 150,
    "Yellow": 150,
    "Green": 200,
    "Dark Blue": 200,
}

group_totals = {
    "Brown": 2,
    "Light Blue": 3,
    "Pink": 3,
    "Orange": 3,
    "Red": 3,
    "Yellow": 3,
    "Green": 3,
    "Dark Blue": 2,
    "Railroad": 4,
    "Utility": 2,
}

group_colors = {
    "Brown": "#8B4513",
    "Light Blue": "#ADD8E6",
    "Pink": "#FFC0CB",
    "Orange": "#FFA500",
    "Red": "#FF0000",
    "Yellow": "#FFFF00",
    "Green": "#008000",
    "Dark Blue": "#00008B",
    "Railroad": "#808080",
    "Utility": "#D3D3D3",
}

mortgage_values = {
    "Mediterranean Avenue": 30,
    "Baltic Avenue": 30,
    "Oriental Avenue": 50,
    "Vermont Avenue": 50,
    "Connecticut Avenue": 60,
    "St. Charles Place": 70,
    "States Avenue": 70,
    "Virginia Avenue": 80,
    "St. James Place": 90,
    "Tennessee Avenue": 90,
    "New York Avenue": 100,
    "Kentucky Avenue": 110,
    "Indiana Avenue": 110,
    "Illinois Avenue": 120,
    "Atlantic Avenue": 130,
    "Ventnor Avenue": 130,
    "Marvin Gardens": 140,
    "Pacific Avenue": 150,
    "North Carolina Avenue": 150,
    "Pennsylvania Avenue": 160,
    "Park Place": 175,
    "Boardwalk": 200,
    "Reading Railroad": 100,
    "Pennsylvania Railroad": 100,
    "B&O Railroad": 100,
    "Short Line Railroad": 100,
    "Electric Company": 75,
    "Water Works": 75,
}

free_parking_jackpot = 0

player_markers = [
    {"shape": "circle", "color": "blue"},
    {"shape": "square", "color": "red"},
    {"shape": "triangle", "color": "green"},
    {"shape": "diamond", "color": "purple"},
]

# =============================================================================
# CHANCE & COMMUNITY CHEST CARDS
# =============================================================================
chance_cards = [
    {"text": "Advance to Go (Collect $200)", "action": "advance_to_go", "amount": 200},
    {
        "text": "Advance to Illinois Avenue",
        "action": "advance_to",
        "target": "Illinois Avenue",
    },
    {
        "text": "Advance token to the nearest Utility",
        "action": "advance_to_nearest_utility",
    },
    {
        "text": "Advance token to the nearest Railroad",
        "action": "advance_to_nearest_railroad",
    },
    {"text": "Bank pays you dividend of $50", "action": "receive_money", "amount": 50},
    {"text": "Get Out of Jail Free", "action": "get_out_of_jail_free"},
    {"text": "Go back 3 spaces", "action": "go_back", "spaces": 3},
    {"text": "Go directly to Jail", "action": "go_to_jail"},
    {
        "text": "Make general repairs on your property – Pay $25 per house",
        "action": "pay_repair",
        "amount": 25,
    },
    {"text": "Pay poor tax of $15", "action": "pay_money", "amount": 15},
    {
        "text": "Take a trip to Reading Railroad",
        "action": "advance_to",
        "target": "Reading Railroad",
    },
    {
        "text": "Take a walk on the Boardwalk",
        "action": "advance_to",
        "target": "Boardwalk",
    },
    {
        "text": "You have been elected Chairman of the Board – Pay each player $50",
        "action": "pay_each",
        "amount": 50,
    },
]

community_chest_cards = [
    {"text": "Advance to Go (Collect $200)", "action": "advance_to_go", "amount": 200},
    {
        "text": "Bank error in your favor – Collect $200",
        "action": "receive_money",
        "amount": 200,
    },
    {"text": "Doctor's fees – Pay $50", "action": "pay_money", "amount": 50},
    {"text": "Get Out of Jail Free", "action": "get_out_of_jail_free"},
    {"text": "Go to Jail", "action": "go_to_jail"},
    {
        "text": "Holiday Fund matures – Receive $100",
        "action": "receive_money",
        "amount": 100,
    },
    {
        "text": "Income tax refund – Collect $20",
        "action": "receive_money",
        "amount": 20,
    },
    {"text": "Hospital Fees – Pay $50", "action": "pay_money", "amount": 50},
    {"text": "School fees – Pay $50", "action": "pay_money", "amount": 50},
    {
        "text": "You are assessed for street repairs – Pay $100",
        "action": "pay_money",
        "amount": 100,
    },
]


# =============================================================================
# PROPERTY CLASS
# =============================================================================
class Property:
    def __init__(self, name, cost, rent, group):
        self.name = name
        self.cost = cost
        self.rent = rent
        self.group = group
        self.owner = None
        self.houses = 0
        self.hotel = False
        self.mortgaged = False

    def __str__(self):
        dev = ""
        if self.hotel:
            dev = "Hotel"
        elif self.houses > 0:
            dev = f"{self.houses} House(s)"
        mort = " (Mortgaged)" if self.mortgaged else ""
        return f"{self.name} ({self.group}) {dev}{mort}".strip()


# =============================================================================
# BOARD CLASS
# =============================================================================
class Board:
    def __init__(self):
        self.spaces = []
        self.create_board()

    def create_board(self):
        self.spaces = [
            "Go",
            Property("Mediterranean Avenue", 60, 2, "Brown"),
            "Community Chest",
            Property("Baltic Avenue", 60, 4, "Brown"),
            "Income Tax",
            Property("Reading Railroad", 200, 25, "Railroad"),
            Property("Oriental Avenue", 100, 6, "Light Blue"),
            "Chance",
            Property("Vermont Avenue", 100, 6, "Light Blue"),
            Property("Connecticut Avenue", 120, 8, "Light Blue"),
            "Jail/Just Visiting",
            Property("St. Charles Place", 140, 10, "Pink"),
            Property("Electric Company", 150, 75, "Utility"),
            Property("States Avenue", 140, 10, "Pink"),
            Property("Virginia Avenue", 160, 12, "Pink"),
            Property("Pennsylvania Railroad", 200, 25, "Railroad"),
            Property("St. James Place", 180, 14, "Orange"),
            "Community Chest",
            Property("Tennessee Avenue", 180, 14, "Orange"),
            Property("New York Avenue", 200, 16, "Orange"),
            "Free Parking",
            Property("Kentucky Avenue", 220, 18, "Red"),
            "Chance",
            Property("Indiana Avenue", 220, 18, "Red"),
            Property("Illinois Avenue", 240, 20, "Red"),
            Property("B&O Railroad", 200, 25, "Railroad"),
            Property("Atlantic Avenue", 260, 22, "Yellow"),
            Property("Ventnor Avenue", 260, 22, "Yellow"),
            Property("Water Works", 150, 75, "Utility"),
            Property("Marvin Gardens", 280, 24, "Yellow"),
            "Go to Jail",
            Property("Pacific Avenue", 300, 26, "Green"),
            Property("North Carolina Avenue", 300, 26, "Green"),
            "Community Chest",
            Property("Pennsylvania Avenue", 320, 28, "Green"),
            Property("Short Line Railroad", 200, 25, "Railroad"),
            "Chance",
            Property("Park Place", 350, 35, "Dark Blue"),
            "Luxury Tax",
            Property("Boardwalk", 400, 50, "Dark Blue"),
        ]

    def size(self):
        return len(self.spaces)


# =============================================================================
# PLAYER CLASS
# =============================================================================
class Player:
    def __init__(self, name, money=1500):
        self.name = name
        self.money = money
        self.position = 0
        self.properties = []
        self.bankrupt = False
        self.in_jail = False
        self.jail_turns = 0

    def mortgage_property(self):
        """Allows player to select a property to mortgage manually for additional cash."""
        available_properties = [prop for prop in self.properties if not prop.mortgaged]

        if not available_properties:
            self.update_info(f"{self.name} has no properties available for mortgage.")
            return

        # Prompt player to choose a property to mortgage
        selected_property = self.prompt_property_choice(available_properties)

        if selected_property:
            selected_property.mortgaged = True
            mortgage_value = mortgage_values[selected_property.name]
            self.money += mortgage_value
            self.update_info(
                f"{self.name} mortgages {selected_property.name} for ${mortgage_value}. New balance: ${self.money}"
            )

    def has_mortgageable_properties(self):
        """Returns True if the player has properties available to mortgage."""
        return any(not prop.mortgaged for prop in self.properties)

    def auto_mortgage(self, required_amount):
        """
        Continuously mortgage properties until the required amount is met.
        Prioritizes lowest-valued properties first to minimize losses.
        """
        while self.money < required_amount and self.has_mortgageable_properties():
            # Sort properties by mortgage value (ascending) to mortgage lowest-valued properties first
            available_properties = sorted(
                [
                    prop
                    for prop in self.properties
                    if not prop.mortgaged and prop.name in mortgage_values
                ],
                key=lambda prop: mortgage_values[prop.name],
            )

            if not available_properties:
                break  # No more properties left to mortgage

            # Mortgage the lowest-valued property
            prop = available_properties[0]
            prop.mortgaged = True
            mortgage_value = mortgage_values[prop.name]
            self.money += mortgage_value
            print(
                f"{self.name} mortgages {prop.name} for ${mortgage_value}. New balance: ${self.money}"
            )

        if self.money < required_amount:
            print(
                f"{self.name} still lacks sufficient funds (${self.money}) after mortgaging all available properties."
            )

    def auto_unmortgage(self):
        """
        Automatically unmortgages properties when sufficient funds are available.
        Prioritizes high-value and high-rent properties first.
        """
        # Sort mortgaged properties by highest rent value, then highest mortgage value
        mortgaged_properties = sorted(
            [prop for prop in self.properties if prop.mortgaged],
            key=lambda prop: (prop.rent, mortgage_values.get(prop.name, 0)),
            reverse=True,
        )

        for prop in mortgaged_properties:
            unmortgage_cost = int(mortgage_values[prop.name] * 1.1)  # 10% interest fee
            if self.money >= unmortgage_cost:
                self.money -= unmortgage_cost
                prop.mortgaged = False
                print(
                    f"{self.name} unmortgages {prop.name} for ${unmortgage_cost}. New balance: ${self.money}"
                )
            else:
                break  # Stop unmortgaging if funds are insufficient

    def process_auction(self, property_obj):
        """Handles an auction, ensuring valid bids and preventing repeated auctions for unsold properties."""
        min_bid = max(property_obj.cost * 0.6, 120)  # Ensure a reasonable starting bid
        self.update_info(f"Auction: {property_obj.name} (Min bid: ${min_bid})")

        # Get list of players who can afford at least the minimum bid and are NOT bankrupt.
        valid_bidders = [
            player
            for player in self.players
            if player.money >= min_bid and not player.bankrupt
        ]

        if not valid_bidders:
            self.update_info(f"No valid bids; {property_obj.name} remains bank-owned.")
            property_obj.owner = None  # Ensure property remains unsold
            return

        # Start auction logic
        current_bid = min_bid
        current_bidder = None
        active_bidders = valid_bidders[:]  # Copy list so we can modify in-loop

        while active_bidders:
            for player in active_bidders:
                # AI behavior for computer players
                if "Computer" in player.name:
                    bid_decision = random.choice(
                        [True, False]
                    )  # Simulated bidding decision
                    bid_amount = (
                        current_bid + random.randint(10, 50) if bid_decision else None
                    )
                else:
                    # Human player: Prompt for bid (adjust for GUI context if needed)
                    bid_amount = self.get_bid_from_player(player, current_bid)

                if bid_amount is None or bid_amount > player.money:
                    active_bidders.remove(
                        player
                    )  # Remove player if they decline or can't afford
                    continue

                # Accept bid and set new highest bidder
                current_bid = bid_amount
                current_bidder = player
                self.update_info(
                    f"{player.name} bids ${current_bid} on {property_obj.name}."
                )

            # Stop auction when only one bidder remains
            if len(active_bidders) == 1 and current_bidder:
                break

        # Finalize auction results
        if current_bidder:
            current_bidder.money -= current_bid
            current_bidder.properties.append(property_obj)
            property_obj.owner = current_bidder
            self.update_info(
                f"{current_bidder.name} wins the auction for {property_obj.name} at ${current_bid}."
            )
        else:
            self.update_info(
                f"Auction ended with no winner; {property_obj.name} remains bank-owned."
            )

    def pay_rent(self, amount, owner):
        """Continuously mortgage properties until rent is fully covered."""
        while self.money < amount and self.has_mortgageable_properties():
            print(
                f"{self.name} needs ${amount} for rent but only has ${self.money}. Attempting to mortgage..."
            )
            self.auto_mortgage(required_amount=amount)

        if self.money >= amount:
            self.money -= amount
            owner.money += amount
            print(f"{self.name} pays ${amount} in rent to {owner.name}.")
        else:
            # If funds remain insufficient even after mortgaging, declare bankruptcy
            owner.money += self.money
            print(f"{self.name} cannot pay rent and is now bankrupt.")
            self.money = 0
            self.declare_bankruptcy()

    def declare_bankruptcy(self, creditor=None):
        """
        Declare bankruptcy and transfer properties to the creditor or bank.
        """
        self.bankrupt = True
        if creditor:
            for prop in self.properties:
                prop.owner = creditor
                creditor.properties.append(prop)
            self.properties.clear()
            print(
                f"{self.name} goes bankrupt and transfers properties to {creditor.name}."
            )
        else:
            for prop in self.properties:
                prop.owner = None
            self.properties.clear()
            print(f"{self.name} goes bankrupt and returns properties to the bank.")


# ===========================================
# AUCTION WINDOW
# =============================================================================
class AuctionWindow(tk.Toplevel):
    def __init__(self, parent, property, players):
        super().__init__(parent)
        self.title("Auction")
        self.property = property
        self.players = players
        self.bids = {}
        self.result = None
        self.build_widgets()
        self.grab_set()
        # Auto-bidding for computer players:
        for p in self.players:
            if "Computer" in p.name and p.money >= self.property.cost:
                max_bid = self.property.cost * random.randint(1, 3)
                bid = random.randint(self.property.cost, max_bid)
                self.bids[p.name] = bid
        self.update_bid_list()

    def build_widgets(self):
        frm = tk.Frame(self, padx=10, pady=10)
        frm.pack()
        tk.Label(
            frm,
            text=f"Auction for {self.property.name}\nMin bid: ${self.property.cost}",
        ).pack()
        self.bid_list = tk.Listbox(frm, width=40)
        self.bid_list.pack(pady=5)
        tk.Label(frm, text="Your Bid:").pack()
        self.bid_entry = tk.Entry(frm)
        self.bid_entry.pack(pady=5)
        tk.Button(frm, text="Submit Bid", command=self.submit_bid).pack(pady=2)
        tk.Button(frm, text="Finish Auction", command=self.finish_auction).pack(pady=2)

    def submit_bid(self):
        human_players = [p for p in self.players if "Computer" not in p.name]
        if not human_players:
            return
        bidder = human_players[0] if len(human_players) == 1 else None
        if not bidder:
            names = [p.name for p in human_players]
            # Release the grab so the dialog can get events.
            self.grab_release()
            choice = simpledialog.askstring(
                "Bidder", f"Enter your name from: {', '.join(names)}"
            )
            bidder = next((p for p in human_players if p.name == choice), None)
            if not bidder:
                messagebox.showinfo("Invalid", "Bidder not found.")
                self.grab_set()  # (Optionally) re-establish the grab if needed.
                return
            self.grab_set()  # Re-establish the grab after finishing with the dialog.
        try:
            bid = int(self.bid_entry.get())
        except ValueError:
            messagebox.showinfo("Invalid", "Enter a valid number for your bid.")
            return
        if bid < self.property.cost or bid > bidder.money:
            messagebox.showinfo(
                "Invalid Bid",
                f"Bid must be at least ${self.property.cost} and no more than your money (${bidder.money}).",
            )
            return
        current_bid = self.bids.get(bidder.name, 0)
        if bid <= current_bid:
            messagebox.showinfo(
                "Invalid", "Your bid must be higher than your previous bid."
            )
            return
        self.bids[bidder.name] = bid
        self.update_bid_list()
        self.bid_entry.delete(0, tk.END)

    def update_bid_list(self):
        self.bid_list.delete(0, tk.END)
        for bidder, bid in self.bids.items():
            self.bid_list.insert(tk.END, f"{bidder}: ${bid}")

    def finish_auction(self):
        if not self.bids:
            self.result = None
        else:
            winner_name = max(self.bids, key=self.bids.get)
            self.result = (winner_name, self.bids[winner_name])
        self.destroy()


# =============================================================================
# DEVELOP WINDOW
# =============================================================================
class DevelopWindow(tk.Toplevel):
    def __init__(self, parent, player):
        super().__init__(parent)
        self.title("Develop Properties")
        self.player = player
        self.result = None
        self.build_widgets()
        self.grab_set()

    def build_widgets(self):
        frm = tk.Frame(self, padx=10, pady=10)
        frm.pack()
        tk.Label(frm, text="Select a property to develop:").pack()
        self.prop_listbox = tk.Listbox(frm, width=50)
        self.prop_listbox.pack(pady=5)
        eligible = []
        groups = {}
        for prop in self.player.properties:
            groups.setdefault(prop.group, []).append(prop)
        for group, props in groups.items():
            if group_totals.get(group, 0) == len(props):
                cost = house_costs.get(group, 0)
                if SHORT_GAME:
                    cost = int(cost * 1.5)  # Increase by 50%
                for prop in props:
                    if (
                        not prop.mortgaged
                        and not prop.hotel
                        and self.player.money >= cost
                    ):
                        eligible.append((prop, cost))
        self.eligible = eligible
        for idx, (prop, cost) in enumerate(eligible):
            dev_status = (
                f"{prop.houses} House(s)" if prop.houses < 4 else "Upgrade to Hotel"
            )
            self.prop_listbox.insert(
                tk.END, f"{prop.name} ({prop.group}) - {dev_status} (Cost: ${cost})"
            )
        btn_frame = tk.Frame(frm)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Develop", command=self.develop_property).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="Cancel", command=self.cancel).pack(
            side=tk.LEFT, padx=5
        )

    def develop_property(self):
        selection = self.prop_listbox.curselection()
        if not selection:
            messagebox.showinfo("Select Property", "Please select a property.")
            return
        idx = selection[0]
        prop, cost = self.eligible[idx]
        if prop.houses < 4:
            if messagebox.askyesno(
                "Build House", f"Build a house on {prop.name} for ${cost}?"
            ):
                prop.houses += 1
                self.player.money -= cost
                self.result = (prop, "house")
        elif prop.houses == 4 and not prop.hotel:
            if messagebox.askyesno(
                "Upgrade to Hotel", f"Upgrade {prop.name} to a hotel for ${cost}?"
            ):
                prop.houses = 0
                prop.hotel = True
                self.player.money -= cost
                self.result = (prop, "hotel")
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


# =============================================================================
# TRADE WINDOW
# =============================================================================
class TradeWindow(tk.Toplevel):
    def __init__(self, parent, current_player, all_players):
        super().__init__(parent)
        self.title("Trade Properties")
        self.current_player = current_player
        self.all_players = all_players
        self.result = None
        self.build_widgets()
        self.grab_set()

    def build_widgets(self):
        frm = tk.Frame(self, padx=10, pady=10)
        frm.pack()
        tk.Label(frm, text="Select one of your properties to trade:").pack()
        self.your_prop_var = tk.StringVar()
        your_props = [
            prop.name for prop in self.current_player.properties if not prop.mortgaged
        ]
        if not your_props:
            tk.Label(frm, text="You have no properties to trade.").pack()
            tk.Button(frm, text="Close", command=self.close).pack(pady=5)
            return
        self.your_prop_var.set(your_props[0])
        tk.OptionMenu(frm, self.your_prop_var, *your_props).pack(pady=5)
        tk.Label(frm, text="Select a property from another player:").pack()
        self.other_prop_var = tk.StringVar()
        other_props = []
        self.target_map = {}
        for p in self.all_players:
            if p != self.current_player:
                for prop in p.properties:
                    if not prop.mortgaged:
                        key = f"{prop.name} (Owner: {p.name})"
                        other_props.append(key)
                        self.target_map[key] = (p, prop)
        if not other_props:
            tk.Label(frm, text="No available properties from others.").pack()
            tk.Button(frm, text="Close", command=self.close).pack(pady=5)
            return
        self.other_prop_var.set(other_props[0])
        tk.OptionMenu(frm, self.other_prop_var, *other_props).pack(pady=5)
        tk.Button(frm, text="Propose Trade", command=self.propose_trade).pack(pady=5)
        tk.Button(frm, text="Cancel", command=self.close).pack(pady=5)

    def propose_trade(self):
        your_prop_name = self.your_prop_var.get()
        other_key = self.other_prop_var.get()
        if not your_prop_name or not other_key:
            messagebox.showinfo("Incomplete", "Select properties for trade.")
            return
        your_prop = next(
            (p for p in self.current_player.properties if p.name == your_prop_name),
            None,
        )
        target_player, target_prop = self.target_map.get(other_key, (None, None))
        if not your_prop or not target_prop:
            messagebox.showinfo("Error", "Property selection error.")
            return
        proposal = f"{self.current_player.name} offers {your_prop.name} for your {target_prop.name}.\nAccept?"
        accepted = False
        if "Computer" in target_player.name:
            accepted = random.choice([True, False])
        else:
            accepted = messagebox.askyesno(
                "Trade Proposal", f"{target_player.name}, " + proposal
            )
        if accepted:
            self.current_player.properties.remove(your_prop)
            target_player.properties.remove(target_prop)
            your_prop.owner = target_player
            target_prop.owner = self.current_player
            self.current_player.properties.append(target_prop)
            target_player.properties.append(your_prop)
            messagebox.showinfo("Trade Accepted", "Trade completed successfully.")
            self.result = (your_prop, target_prop)
        else:
            messagebox.showinfo("Trade Rejected", "Trade was rejected.")
            self.result = None
        self.destroy()

    def close(self):
        self.result = None
        self.destroy()


# =============================================================================
# MONOPOLY GUI IMPLEMENTATION – PART 3A
# =============================================================================
class MonopolyGUI:
    def __init__(self, players):
        self.unsold_properties = []
        self.root = tk.Tk()
        self.game_over = False  # Add this line to indicate the game is active
        self.root.title("Monopoly Game")
        # Two columns: left - board area (canvas with log overlay), right - player info.
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)

        self.players = players
        self.auto_mode = all("Computer" in p.name for p in self.players)
        self.turn_count = 0

        # Board area
        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid(row=0, column=0, sticky="nsew")
        canvas_width = MARGIN * 2 + CELL_SIZE * 11
        canvas_height = MARGIN * 2 + CELL_SIZE * 11
        self.canvas = tk.Canvas(
            self.board_frame, width=canvas_width, height=canvas_height
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Motion>", self.on_canvas_motion)

        # Create the log overlay as a child of the canvas and place it in the center.
        self.log_frame = tk.Frame(self.canvas, bg="white", bd=3, relief="ridge")
        self.log_text = ScrolledText(
            self.log_frame, width=60, height=12, font=("Arial", 10)
        )
        self.log_text.pack()
        self.canvas.create_window(
            canvas_width / 2,
            canvas_height / 2,
            window=self.log_frame,
            tags="log_window",
        )

        # Player info area
        self.info_frame = tk.Frame(self.root)
        self.info_frame.grid(row=0, column=1, sticky="nsew")
        self.player_info_texts = []
        for idx, player in enumerate(self.players):
            lf = tk.LabelFrame(
                self.info_frame, text=f"Player {idx+1}: {player.name}", padx=5, pady=5
            )
            lf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            st = ScrolledText(lf, wrap=tk.WORD, width=30, height=10, font=("Arial", 10))
            st.pack(fill=tk.BOTH, expand=True)
            self.player_info_texts.append(st)

        # Control buttons area
        control_frame = tk.Frame(self.root)
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.info_label = tk.Label(control_frame, text="", font=("Arial", 14))
        self.info_label.pack(pady=5)
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(pady=5)
        self.roll_button = tk.Button(
            btn_frame, text="Roll Dice", command=self.roll_turn
        )
        self.roll_button.pack(side=tk.LEFT, padx=5)
        self.develop_button = tk.Button(
            btn_frame, text="Develop Properties", command=self.develop_properties
        )
        self.develop_button.pack(side=tk.LEFT, padx=5)
        self.trade_button = tk.Button(
            btn_frame, text="Trade", command=self.trade_properties
        )
        self.trade_button.pack(side=tk.LEFT, padx=5)
        self.save_button = tk.Button(
            btn_frame, text="Save Game", command=self.save_game
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.load_button = tk.Button(
            btn_frame, text="Load Game", command=self.load_game
        )
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.exit_button = tk.Button(
            btn_frame, text="Save & Exit", command=self.save_and_exit
        )
        self.exit_button.pack(side=tk.LEFT, padx=5)
        self.create_mortgage_button()  # Add this inside MonopolyGUI.__init__()
        self.create_unmortgage_button()  # Add this inside MonopolyGUI.__init__()

        self.board = Board()
        self.current_player = 0
        self.current_tooltip = None

        self.draw_board()
        self.update_board()
        if self.players:
            self.update_info(f"{self.players[0].name}'s turn.")
        else:
            self.update_info("Game loaded. Click Roll Dice to continue.")
        self.update_player_info_panel()
        self.update_control_buttons()

        # If there are players and it's the computer's turn, auto-roll.
        if self.players:
            current = self.players[self.current_player]
            if self.auto_mode or "Computer" in current.name:
                self.root.after(1000, self.roll_turn)

    def create_unmortgage_button(self):
        """Adds a button to allow players to unmortgage properties manually."""
        self.unmortgage_button = tk.Button(
            self.root, text="Unmortgage Property", command=self.player_unmortgage_action
        )
        self.unmortgage_button.grid(
            row=2, column=1, pady=5
        )  # Position next to mortgage button

    def create_mortgage_button(self):
        """Adds a button to allow players to mortgage properties manually."""
        self.mortgage_button = tk.Button(
            self.root, text="Mortgage Property", command=self.player_mortgage_action
        )
        self.mortgage_button.grid(row=2, column=0, pady=5)  # Use grid instead of pack

    def player_unmortgage_action(self):
        """Handles manual unmortgaging when the player presses the unmortgage button."""
        player = self.players[self.current_player]
        mortgaged_properties = [prop for prop in player.properties if prop.mortgaged]

        if not mortgaged_properties:
            self.update_info(
                f"{player.name} has no mortgaged properties to unmortgage."
            )
            return

        # Prompt player to choose a property to unmortgage
        selected_name = simpledialog.askstring(
            "Unmortgage Property",
            f"Enter the name of the property to unmortgage: {', '.join([p.name for p in mortgaged_properties])}",
        )

        selected_property = next(
            (prop for prop in mortgaged_properties if prop.name == selected_name), None
        )

        if selected_property:
            unmortgage_cost = int(
                mortgage_values[selected_property.name] * 1.1
            )  # 10% interest
            if player.money >= unmortgage_cost:
                selected_property.mortgaged = False  # ✅ Property stays with player
                player.money -= unmortgage_cost
                self.update_info(
                    f"{player.name} unmortgages {selected_property.name} for ${unmortgage_cost}. New balance: ${player.money}. Rent collection resumes!"
                )
                self.update_player_info_panel()  # Refresh UI after unmortgage
            else:
                self.update_info(
                    f"{player.name} does not have enough funds to unmortgage {selected_property.name}."
                )

    def player_mortgage_action(self):
        """Handles manual mortgaging when the player presses the mortgage button."""
        player = self.players[self.current_player]
        available_properties = [
            prop for prop in player.properties if not prop.mortgaged
        ]

        if not available_properties:
            self.update_info(f"{player.name} has no properties available to mortgage.")
            return

        selected_name = simpledialog.askstring(
            "Mortgage Property",
            f"Enter the name of the property to mortgage: {', '.join([p.name for p in available_properties])}",
        )
        selected_property = next(
            (prop for prop in available_properties if prop.name == selected_name), None
        )

        if selected_property:
            selected_property.mortgaged = True
            mortgage_value = mortgage_values[selected_property.name]
            player.money += mortgage_value
            self.update_info(
                f"{player.name} mortgages {selected_property.name} for ${mortgage_value}. New balance: ${player.money}"
            )
            self.update_player_info_panel()

    def should_buy_property(self, player, prop):
        # Avoid groups where opponents already own
        if any(
            p != player and any(pp.group == prop.group for pp in p.properties)
            for p in self.players
        ):
            return False

        # Check ownership in the group
        owns_group = any(p.group == prop.group for p in player.properties)
        reserve = (
            300 if owns_group else 500
        )  # Increased reserve for more conservative play

        return player.money >= prop.cost + reserve

    def execute_card_action(self, player, card):
        global free_parking_jackpot
        act = card.get("action", "")

        if act == "advance_to_go":
            player.position = 0
            amt = card.get("amount", 0)
            player.money += amt
            self.update_info(f"{player.name} advances to Go and collects ${amt}.")

        elif act == "advance_to":
            target = card.get("target", "")
            for idx, space in enumerate(self.board.spaces):
                if isinstance(space, Property) and space.name == target:
                    player.position = idx
                    self.update_info(f"{player.name} advances to {target}.")
                    # ✅ Check property ownership and give buying option
                    if space.owner is None:
                        if "Computer" in player.name:
                            if self.should_buy_property(player, space):
                                player.money -= space.cost
                                space.owner = player
                                player.properties.append(space)
                                self.update_info(
                                    f"{player.name} buys {space.name} for ${space.cost}."
                                )
                        else:
                            ans = messagebox.askquestion(
                                "Buy Property",
                                f"Would you like to buy {space.name} for ${space.cost}?",
                            )
                            if ans == "yes" and player.money >= space.cost:
                                player.money -= space.cost
                                space.owner = player
                                player.properties.append(space)
                                self.update_info(
                                    f"{player.name} buys {space.name} for ${space.cost}."
                                )
                            else:
                                self.update_info(
                                    f"{player.name} chose not to buy {space.name}."
                                )
                    else:
                        # ✅ Property is owned—pay rent
                        rent_due = (
                            space.rent
                            if not SHORT_GAME
                            else int(space.rent * RENT_MULTIPLIER)
                        )
                        self.update_info(
                            f"{player.name} lands on {space.name}, owned by {space.owner.name}. Pays ${rent_due} in rent."
                        )
                        player.pay_rent(rent_due, space.owner)
                    break

        elif act == "advance_to_nearest_utility":
            pos = player.position
            for i in range(1, self.board.size()):
                idx = (pos + i) % self.board.size()
                space = self.board.spaces[idx]
                if isinstance(space, Property) and space.group == "Utility":
                    player.position = idx
                    self.update_info(f"{player.name} advances to the nearest Utility.")
                    if space.owner is None:
                        if self.should_buy_property(player, space):
                            player.money -= space.cost
                            space.owner = player
                            player.properties.append(space)
                            self.update_info(
                                f"{player.name} buys {space.name} for ${space.cost}."
                            )
                    else:
                        rent_due = 10 * (random.randint(1, 6) + random.randint(1, 6))
                        self.update_info(
                            f"{player.name} must pay ${rent_due} rent to {space.owner.name}."
                        )
                        player.pay_rent(rent_due, space.owner)
                    break

        elif act == "advance_to_nearest_railroad":
            pos = player.position
            for i in range(1, self.board.size()):
                idx = (pos + i) % self.board.size()
                space = self.board.spaces[idx]
                if isinstance(space, Property) and space.group == "Railroad":
                    player.position = idx
                    self.update_info(f"{player.name} advances to the nearest Railroad.")
                    if space.owner is None:
                        if self.should_buy_property(player, space):
                            player.money -= space.cost
                            space.owner = player
                            player.properties.append(space)
                            self.update_info(
                                f"{player.name} buys {space.name} for ${space.cost}."
                            )
                    else:
                        rent_due = space.rent * 2
                        self.update_info(
                            f"{player.name} must pay ${rent_due} rent to {space.owner.name}."
                        )
                        player.pay_rent(rent_due, space.owner)
                    break

        elif act == "go_back":
            spaces = card.get("spaces", 0)
            player.position = (player.position - spaces) % self.board.size()
            self.update_info(f"{player.name} goes back {spaces} spaces.")

        elif act == "go_to_jail":
            player.position = 10  # Move to Jail space
            player.in_jail = True  # Ensure they are in jail
            player.jail_turns = 0  # Reset jail turn count
            self.update_info(
                f"{player.name} is sent to Jail! They must roll doubles or pay to escape."
            )
            self.update_board()
            return  # Stop further actions for this turn

        elif act == "receive_money":
            amt = card.get("amount", 0)
            player.money += amt
            self.update_info(f"{player.name} receives ${amt}.")

        elif act == "pay_money":
            amt = card.get("amount", 0)
            if player.money >= amt:
                player.money -= amt
                free_parking_jackpot += amt
                self.update_info(f"{player.name} pays ${amt}.")
            else:
                print(
                    f"{player.name} needs ${amt} for taxes but only has ${player.money}. Attempting to mortgage..."
                )
                player.auto_mortgage(required_amount=amt)

                if player.money >= amt:
                    player.money -= amt
                    free_parking_jackpot += amt
                    print(
                        f"After mortgaging, {player.name} pays ${amt} in taxes to the bank."
                    )
                else:
                    # If funds remain insufficient even after mortgaging, declare bankruptcy
                    free_parking_jackpot += player.money
                    print(f"{player.name} cannot pay rent and is now bankrupt.")
                    player.money = 0
                    player.declare_bankruptcy()

        elif act == "get_out_of_jail_free":
            self.update_info(f"{player.name} gets a Get Out of Jail Free card.")

        elif act == "pay_repair":
            house_cost = card.get("house_amount", 0)
            hotel_cost = card.get("hotel_amount", 0)
            total = sum(
                house_cost * p.houses + (hotel_cost if p.hotel else 0)
                for p in player.properties
            )
            player.money -= total
            self.update_info(f"{player.name} pays ${total} for property repairs.")

        elif act == "pay_each":
            amt = card.get("amount", 0)
            for p in self.players:
                if p != player:
                    p.money -= amt
                    player.money += amt
            self.update_info(f"{player.name} collects ${amt} from each player.")

        else:
            self.update_info("Card action not recognized.")

    def on_canvas_motion(self, event):
        # Get the items under the current mouse pointer.
        current_items = self.canvas.find_withtag("current")
        if current_items:
            tags = self.canvas.gettags(current_items[0])
            # Check if any tag indicates that this is a board space (e.g., "space_X").
            if any(tag.startswith("space_") for tag in tags):
                return  # The mouse is over a property, so do nothing.
        # Otherwise, if a tooltip exists, hide it.
        if self.current_tooltip:
            self.current_tooltip.hide()
            self.current_tooltip = None

    def log_event(self, msg):
        try:
            # Write to GUI log
            if self.log_text and self.log_text.winfo_exists():
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
        except tk.TclError:
            pass

        # Write to file
        try:
            with open(LOG_FILE, "a") as f:
                f.write(msg + "\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")

    def play_sound(self, sound_type="default"):
        try:
            import winsound

            if sound_type == "roll":
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            elif sound_type == "buy":
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            elif sound_type == "auction":
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
            else:
                winsound.PlaySound("SystemDefault", winsound.SND_ALIAS)
        except Exception:
            pass

    def update_control_buttons(self):
        if not self.players or not hasattr(self, "roll_button"):
            return

        # Check if roll_button exists and hasn't been destroyed
        try:
            if self.roll_button.winfo_exists():
                current = self.players[self.current_player]
                if "Computer" in current.name:
                    self.roll_button.config(state=tk.DISABLED)
                    self.develop_button.config(state=tk.DISABLED)
                    self.trade_button.config(state=tk.DISABLED)
                else:
                    self.roll_button.config(state=tk.NORMAL)
                    self.develop_button.config(state=tk.NORMAL)
                    self.trade_button.config(state=tk.NORMAL)
        except tk.TclError:
            # One of the buttons has been destroyed; do nothing
            return

    def update_player_info_panel(self):
        for idx, player in enumerate(self.players):
            info = f"Money: ${player.money}\nPosition: {player.position}\nProperties:\n"
            if player.properties:
                for prop in player.properties:
                    dev = ""
                    if prop.hotel:
                        dev = " (Hotel)"
                    elif prop.houses:
                        dev = f" ({prop.houses} House{'s' if prop.houses > 1 else ''})"
                    mort = " (Mortgaged)" if prop.mortgaged else ""
                    info += f"- {prop.name} [{prop.group}]{dev}{mort}\n"
            else:
                info += "None\n"
            self.player_info_texts[idx].delete("1.0", tk.END)
            self.player_info_texts[idx].insert(tk.END, info)

    def update_info(self, text):
        timestamp = datetime.datetime.now().strftime(
            "[%Y-%m-%d %H:%M:%S]"
        )  # Format: [YYYY-MM-DD HH:MM:SS]
        message_with_timestamp = f"{timestamp} {text}"

        try:
            if self.info_label and self.info_label.winfo_exists():
                self.info_label.config(text=message_with_timestamp)
        except tk.TclError:
            pass  # The widget may have been destroyed, ignore

        self.log_event(message_with_timestamp)  # Ensure logs also include timestamps

    def get_space_coords(self, index):
        s = CELL_SIZE
        m = MARGIN
        if 0 <= index <= 10:
            x = m + (10 - index) * s
            y = m + 10 * s
        elif 10 < index <= 20:
            x = m
            y = m + (20 - index) * s
        elif 20 < index <= 30:
            x = m + (index - 20) * s
            y = m
        elif 30 < index < 40:
            x = m + 10 * s
            y = m + (index - 30) * s
        else:
            x, y = m, m
        return x, y, s, s

    def draw_board(self):
        if not self.canvas.winfo_exists():
            return
        self.canvas.delete("board_items")
        for i in range(self.board.size()):
            x, y, w, h = self.get_space_coords(i)
            space = self.board.spaces[i]
            if isinstance(space, Property):
                fill = group_colors.get(space.group, "white")
                self.canvas.create_rectangle(
                    x,
                    y,
                    x + w,
                    y + h,
                    fill=fill,
                    outline="black",
                    tags=("board_items", f"space_{i}"),
                )
                self.canvas.create_text(
                    x + w / 2,
                    y + h / 2,
                    text=f"{space.name}\n${space.cost}",
                    font=("Arial", 8),
                    width=w,
                    tags=("board_items",),
                )
            else:
                self.canvas.create_rectangle(
                    x,
                    y,
                    x + w,
                    y + h,
                    fill="white",
                    outline="black",
                    tags=("board_items", f"space_{i}"),
                )
                self.canvas.create_text(
                    x + w / 2,
                    y + h / 2,
                    text=space,
                    font=("Arial", 8),
                    width=w,
                    tags=("board_items",),
                )
            self.canvas.tag_bind(f"space_{i}", "<Enter>", self.on_space_enter)
            self.canvas.tag_bind(f"space_{i}", "<Leave>", self.on_space_leave)
        self.draw_player_markers()

    def draw_player_markers(self):
        for idx, player in enumerate(self.players):
            marker = player_markers[idx % len(player_markers)]
            x, y, w, h = self.get_space_coords(player.position)
            if marker["shape"] == "circle":
                self.canvas.create_oval(
                    x + 10,
                    y + 10,
                    x + 40,
                    y + 40,
                    fill=marker["color"],
                    outline="",
                    tags="board_items",
                )
            elif marker["shape"] == "square":
                self.canvas.create_rectangle(
                    x + 10,
                    y + 10,
                    x + 40,
                    y + 40,
                    fill=marker["color"],
                    outline="",
                    tags="board_items",
                )
            elif marker["shape"] == "triangle":
                self.canvas.create_polygon(
                    [x + 25, y + 10, x + 10, y + 40, x + 40, y + 40],
                    fill=marker["color"],
                    outline="",
                    tags="board_items",
                )
            elif marker["shape"] == "diamond":
                self.canvas.create_polygon(
                    [x + 25, y + 10, x + 10, y + 25, x + 25, y + 40, x + 40, y + 25],
                    fill=marker["color"],
                    outline="",
                    tags="board_items",
                )

    def on_space_enter(self, event):
        # Get the tags for the current canvas item.
        tags = self.canvas.gettags("current")
        details = ""
        for tag in tags:
            if tag.startswith("space_"):
                idx = int(tag.split("_")[1])
                space = self.board.spaces[idx]
                if isinstance(space, Property):
                    details = f"{space.name}\nCost: ${space.cost}\nRent: ${space.rent}\nGroup: {space.group}"
                    if space.hotel:
                        details += "\nDeveloped: Hotel"
                    elif space.houses:
                        details += f"\nDeveloped: {space.houses} House(s)"
                    if space.mortgaged:
                        details += "\nStatus: Mortgaged"
                else:
                    details = str(space)
                break  # Found the relevant space; no need to check further.
        # Get current pointer coordinates relative to the window.
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()
        # Hide any existing tooltip before displaying a new one.
        if self.current_tooltip:
            self.current_tooltip.hide()
        self.current_tooltip = Tooltip(self.canvas, details)
        self.current_tooltip.show(x, y)

    def on_space_leave(self, event):
        if self.current_tooltip:
            self.current_tooltip.hide()
            self.current_tooltip = None

    def animate_move(self, player, steps, callback):
        if self.game_over:
            return
        if steps > 0:
            old = player.position
            new = (old + 1) % self.board.size()
            # Check if the player passed GO.
            if new < old:
                bonus = 100 if SHORT_GAME else 200
                player.money += bonus
                self.update_info(f"{player.name} passed Go and collects ${bonus}.")
            player.position = new
            self.update_board()
            self.root.after(300, lambda: self.animate_move(player, steps - 1, callback))
        else:
            callback()

    def update_board(self):
        # If the game is over, do nothing.
        if self.game_over:
            return
        try:
            if not (self.root.winfo_exists() and self.canvas.winfo_exists()):
                return
            self.draw_board()
            self.update_player_info_panel()
        except tk.TclError:
            # If widgets have been destroyed, silently exit.
            return

    def after_move(self, player):
        self.process_space(player)

        if player.bankrupt:
            self.check_bankruptcy(player)
            self.root.after(1000, self.next_turn)
            return

        if "Computer" in player.name:
            self.auto_develop(player)
            player.auto_unmortgage()
            self.root.after(1000, self.next_turn)
        else:
            self.update_control_buttons()
            self.root.after(
                1000, self.next_turn
            )  # ✅ FIX: Continue game after human's turn

    def process_space(self, player):
        space = self.board.spaces[player.position]
        global free_parking_jackpot

        if isinstance(space, Property):
            if space.owner is None:
                if "Computer" in player.name:
                    if not self.should_buy_property(player, space):
                        self.start_auction(space)
                    else:
                        player.money -= space.cost
                        space.owner = player
                        player.properties.append(space)
                        self.update_info(
                            f"{player.name} buys {space.name} for ${space.cost}."
                        )
                else:
                    ans = messagebox.askquestion(
                        "Buy Property",
                        f"Would you like to buy {space.name} for ${space.cost}?",
                    )
                    if ans == "yes" and player.money >= space.cost:
                        player.money -= space.cost
                        space.owner = player
                        player.properties.append(space)
                        self.update_info(
                            f"{player.name} buys {space.name} for ${space.cost}."
                        )
                    else:
                        self.start_auction(space)
            elif space.owner == player:
                self.update_info(f"{player.name} already owns {space.name}.")
            else:
                rent = (
                    space.rent if not SHORT_GAME else int(space.rent * RENT_MULTIPLIER)
                )
                self.update_info(
                    f"{player.name} must pay rent of ${rent} to {space.owner.name}."
                )
                player.pay_rent(rent, space.owner)

        elif space == "Chance":
            card = random.choice(chance_cards)
            self.update_info(f"Chance: {card['text']}")
            self.execute_card_action(player, card)

        elif space == "Community Chest":
            card = random.choice(community_chest_cards)
            self.update_info(f"Community Chest: {card['text']}")
            self.execute_card_action(player, card)

        elif space == "Income Tax":
            tax = amount = 200
            if player.money >= 200:
                player.money -= tax
                free_parking_jackpot += tax
                self.update_info(f"{player.name} pays Income Tax of ${tax}.")
            else:
                print(
                    f"{player.name} needs $200 for taxes but only has ${player.money}. Attempting to mortgage..."
                )
                self.auto_mortgage(required_amount=amount)

                if player.money >= amount:
                    player.money -= amount
                    free_parking_jackpot += amount
                    print(
                        f"After mortgaging, {player.name} pays ${amount} in taxes to the bank."
                    )
                else:
                    # If funds remain insufficient even after mortgaging, declare bankruptcy
                    free_parking_jackpot += player.money
                    print(f"{player.name} cannot pay rent and is now bankrupt.")
                    player.money = 0
                    player.declare_bankruptcy()
        elif space == "Luxury Tax":
            tax = amount = 75
            if player.money >= 75:
                player.money -= tax
                free_parking_jackpot += tax
                self.update_info(f"{player.name} pays Luxury Tax of ${tax}.")
            else:
                print(
                    f"{player.name} needs $75 for taxes but only has ${player.money}. Attempting to mortgage..."
                )
                player.auto_mortgage(required_amount=amount)

                if player.money >= amount:
                    player.money -= amount
                    free_parking_jackpot += amount
                    print(
                        f"After mortgaging, {player.name} pays ${amount} in taxes to the bank."
                    )
                else:
                    # If funds remain insufficient even after mortgaging, declare bankruptcy
                    owner.money += player.money
                    print(f"{player.name} cannot pay rent and is now bankrupt.")
                    player.money = 0
                    player.declare_bankruptcy()

        elif space == "Free Parking":
            if not SHORT_GAME:
                self.update_info(
                    f"{player.name} collects ${free_parking_jackpot} from Free Parking!"
                )
                player.money += free_parking_jackpot
                free_parking_jackpot = 0
            else:
                self.update_info("Short Game: Free Parking has no payout.")
        elif space == "Go to Jail":
            self.update_info(f"{player.name} is sent to Jail!")
            player.position = 10  # Jail space
            player.in_jail = True
            player.jail_turns = 0
            self.update_board()
            return

        # Check for bankruptcy
        if player.money <= 0:
            creditor = space.owner if isinstance(space, Property) else None
            player.declare_bankruptcy(creditor)
            self.end_game()
            return

        self.update_board()

    def start_auction(self, property):
        # Determine eligible bidders
        eligible_bidders = [p for p in self.players if p.money > 0 and not p.bankrupt]
        if not eligible_bidders:
            self.update_info(
                f"Auction skipped: no players can afford {property.name} (Cost: ${property.cost})."
            )
            if property not in self.unsold_properties:
                self.unsold_properties.append(property)
            return

        # Auto-auction if all are computer players
        all_computers = all("Computer" in p.name for p in eligible_bidders)
        if all_computers:
            self.update_info(
                f"Auction (Auto): {property.name} (Min bid: ${property.cost})"
            )
            bids = {}
            for p in eligible_bidders:
                max_bid = min(p.money, property.cost * random.randint(1, 3))
                bid = random.randint(property.cost, max_bid)
                bids[p.name] = bid

            if not bids:
                self.update_info("No valid bids; property remains unsold.")
                if property not in self.unsold_properties:
                    self.unsold_properties.append(property)
                return

            winner_name = max(bids, key=bids.get)
            bid_amount = bids[winner_name]
            winner = next(p for p in eligible_bidders if p.name == winner_name)
            winner.money -= bid_amount
            property.owner = winner
            winner.properties.append(property)
            self.update_info(f"{winner.name} wins {property.name} at ${bid_amount}.")
            self.update_board()
            return

        # Human auction window
        self.update_info(f"Auction: {property.name} (Min bid: ${property.cost}).")
        auction = AuctionWindow(self.root, property, eligible_bidders)
        self.root.wait_window(auction)

        if auction.result:
            winner_name, bid = auction.result
            winner = next(p for p in eligible_bidders if p.name == winner_name)
            winner.money -= bid
            property.owner = winner
            winner.properties.append(property)
            self.update_info(f"{winner.name} wins {property.name} at ${bid}.")
        else:
            self.update_info("No valid bids; property remains unsold.")
            if property not in self.unsold_properties:
                self.unsold_properties.append(property)

        self.update_board()

    def develop_properties(self):
        current = self.players[self.current_player]
        if "Computer" in current.name:
            self.update_info("Computer players auto-develop properties.")
            return
        win = DevelopWindow(self.root, current)
        self.root.wait_window(win)
        if win.result:
            prop, dtype = win.result
            self.update_info(f"{current.name} develops {prop.name}: {dtype}.")
            self.update_board()

    def trade_properties(self):
        current = self.players[self.current_player]
        if "Computer" in current.name:
            self.update_info("Computer players do not trade manually.")
            return
        tw = TradeWindow(self.root, current, self.players)
        self.root.wait_window(tw)
        if tw.result:
            self.update_board()

    def auto_develop(self, player):
        groups = {}
        for p in player.properties:
            groups.setdefault(p.group, []).append(p)

        for group, props in groups.items():
            if len(props) == group_totals.get(group, 0):
                cost = house_costs.get(group, 0)
                if SHORT_GAME:
                    cost = int(cost * 1.5)  # Increase by 50%

                for p in props:
                    if not p.hotel and p.houses < 4:
                        if player.money >= cost:
                            player.money -= cost
                            p.houses += 1
                            self.update_info(
                                f"{player.name} builds a house on {p.name} (Total: {p.houses})."
                            )
                        else:
                            self.update_info(
                                f"{player.name} does not have enough money to develop {p.name}."
                            )

                    elif p.houses == 4 and not p.hotel:
                        if player.money >= cost:
                            player.money -= cost
                            p.houses = 0
                            p.hotel = True
                            self.update_info(
                                f"{player.name} upgrades {p.name} to a hotel."
                            )
                        else:
                            self.update_info(
                                f"{player.name} does not have enough money to upgrade {p.name} to a hotel."
                            )

        self.update_board()

    def check_bankruptcy(self, player):
        if player.bankrupt:
            creditor = None  # Determine the creditor (if any) based on game logic here.
            player.declare_bankruptcy(creditor)

            # Remove the bankrupt player from the game.
            self.update_info(f"{player.name} is bankrupt and eliminated!")

            if player in self.players:
                self.players.remove(player)

            # Adjust current_player index after removing a player.
            if self.current_player >= len(self.players):
                self.current_player = 0

            # Check for game end condition.
            if len(self.players) == 1:
                winner_name = self.players[0].name
                final_message = f"Winner: {winner_name}\n\n"

                final_message += f"{self.players[0].name} is the winner!"

                messagebox.showinfo("Game Over", final_message)

                # Optionally, close the game after a delay.
                self.root.after(5000, self.root.destroy)

    def next_turn(self):
        """Move to the next turn, skipping bankrupt players & ensuring correct rotation."""
        self.players = [
            p for p in self.players if not p.bankrupt
        ]  # Remove bankrupt players
        if len(self.players) <= 1:
            self.end_game()
            return

        # Advance turn index with a check for non-bankrupt players
        self.current_player = (self.current_player + 1) % len(self.players)

        self.turn_count += 1
        self.update_info(
            f"----- Turn {self.turn_count}: {self.players[self.current_player].name}'s turn -----"
        )

        # Ensure bankrupt players are NOT allowed back in rotation
        while self.players[self.current_player].bankrupt:
            self.current_player = (self.current_player + 1) % len(self.players)

        self.update_player_info_panel()
        self.update_control_buttons()

        if "Computer" in self.players[self.current_player].name:
            self.root.after(500, self.roll_turn)

    def end_game(self):
        self.game_over = True
        # Build final standings and calculate net worth.
        standings = []
        for p in self.players:
            prop_val = sum(
                prop.cost for prop in p.properties if isinstance(prop, Property)
            )
            net = p.money + prop_val
            standings.append((p, net))
        standings.sort(key=lambda tup: tup[1], reverse=True)

        # Create and display the final statistics window.
        final_stats = FinalStatsWindow(self.root, standings)
        self.root.wait_window(final_stats)

        # When FinalStatsWindow is closed, destroy the main window.
        self.root.destroy()

    def save_game(self):
        state = {
            "players": [
                {
                    "name": p.name,
                    "money": p.money,
                    "position": p.position,
                    "properties": [
                        {
                            "name": prop.name,
                            "mortgaged": prop.mortgaged,
                            "houses": prop.houses,
                            "hotel": prop.hotel,
                        }
                        for prop in p.properties
                    ],
                }
                for p in self.players
            ],
            "current_player": self.current_player,
            "free_parking_jackpot": free_parking_jackpot,
            "turn_count": self.turn_count,
        }
        with open("monopoly_save.json", "w") as f:
            json.dump(state, f)
        self.update_info("Game saved successfully.")

    def load_game(self):
        global free_parking_jackpot
        try:
            with open("monopoly_save.json", "r") as f:
                state = json.load(f)
            self.players = []
            for p in state["players"]:
                print(f"Loading player: {p}")  # Debugging statement
                player = Player(p["name"], p["money"])
                player.position = p["position"]
                player.properties = []
                # p["properties"] is a list of dicts.
                for prop_data in p["properties"]:
                    print(f"Loading property: {prop_data}")  # Debugging statement
                    for sp in self.board.spaces:
                        if isinstance(sp, Property) and sp.name == prop_data["name"]:
                            sp.owner = player
                            sp.mortgaged = prop_data.get("mortgaged", False)
                            sp.houses = prop_data.get("houses", 0)
                            sp.hotel = prop_data.get("hotel", False)
                            player.properties.append(sp)
                            break
                self.players.append(player)
            self.current_player = state["current_player"]
            free_parking_jackpot = state["free_parking_jackpot"]
            self.turn_count = state.get("turn_count", 0)
            self.update_info("Game loaded successfully.")

            # Rebuild the player info panel with the loaded players.
            for widget in self.info_frame.winfo_children():
                widget.destroy()
            self.player_info_texts = []
            for idx, player in enumerate(self.players):
                lf = tk.LabelFrame(
                    self.info_frame,
                    text=f"Player {idx+1}: {player.name}",
                    padx=5,
                    pady=5,
                )
                lf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                st = ScrolledText(
                    lf, wrap=tk.WORD, width=30, height=10, font=("Arial", 10)
                )
                st.pack(fill=tk.BOTH, expand=True)
                self.player_info_texts.append(st)

            self.update_board()

            # Recalculate auto_mode based on the loaded players
            self.auto_mode = all("Computer" in p.name for p in self.players)
        except FileNotFoundError:
            messagebox.showerror("Load Game", "No saved game file found!")
        except Exception as e:
            print(f"Error loading game: {e}")  # Debugging statement

    def save_and_exit(self):
        self.save_game()
        self.root.destroy()

    def mainloop(self):
        self.root.mainloop()

    def roll_turn(self):
        player = self.players[self.current_player]

        # Jail check
        if player.in_jail:
            die1 = random.randint(1, 6)
            die2 = random.randint(1, 6)
            self.update_info(f"{player.name} rolls {die1} and {die2} in jail.")
            if die1 == die2:
                self.update_info(f"{player.name} rolls doubles and escapes jail!")
                player.in_jail = False
                player.jail_turns = 0
                total = die1 + die2
                self.animate_move(player, total, lambda: self.after_move(player))
            else:
                player.jail_turns += 1
                if player.jail_turns >= 3:
                    self.update_info(
                        f"{player.name} failed to roll doubles in 3 turns and now must move."
                    )
                    player.in_jail = False
                    player.jail_turns = 0
                    total = die1 + die2
                    self.animate_move(player, total, lambda: self.after_move(player))
                else:
                    self.root.after(1000, self.next_turn)
            return

        # Standard roll
        total = random.randint(1, 6) + random.randint(1, 6)
        self.update_info(f"{player.name} rolled a {total}.")
        self.animate_move(player, total, lambda: self.after_move(player))


# =============================================================================
# TOOLTIP CLASS
# =============================================================================
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.top = None

    def show(self, x, y):
        if self.top or not self.text:
            return
        self.top = tk.Toplevel(self.widget)
        self.top.wm_overrideredirect(True)
        self.top.wm_geometry(f"+{x+20}+{y+20}")
        label = tk.Label(
            self.top,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 8),
        )
        label.pack()

    def hide(self):
        if self.top:
            self.top.destroy()
            self.top = None


class FinalStatsWindow(tk.Toplevel):
    def __init__(self, parent, standings):
        super().__init__(parent)
        self.title("Final Game Statistics")
        # Make sure the window cannot be resized (optional)
        self.resizable(False, False)
        self.standings = standings
        self.build_widgets()
        self.grab_set()  # Make this window modal

    def build_widgets(self):
        frm = tk.Frame(self, padx=10, pady=10)
        frm.pack(fill=tk.BOTH, expand=True)

        st = ScrolledText(frm, width=60, height=20, font=("Arial", 10))
        st.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        message = self.generate_stats_text()
        st.insert(tk.END, message)
        st.config(state=tk.DISABLED)  # Make the text read-only

        btn = tk.Button(frm, text="OK", command=self.on_ok)
        btn.pack(pady=10)

    def generate_stats_text(self):
        message = "Game Over!\n\nFinal Standings:\n\n"
        for player, net in self.standings:
            message += f"Player: {player.name}\n"
            message += f"  Money: ${player.money}\n"
            message += f"  Property Count: {len(player.properties)}\n"
            message += f"  Net Worth (Money + Property Costs): ${net}\n"
            if player.properties:
                message += "  Properties:\n"
                for prop in player.properties:
                    details = f"    - {prop.name} (Cost: ${prop.cost}, Rent: ${prop.rent}, Group: {prop.group}"
                    if prop.mortgaged:
                        details += ", Mortgaged"
                    if prop.houses > 0:
                        details += f", Houses: {prop.houses}"
                    if prop.hotel:
                        details += ", Hotel"
                    details += ")\n"
                    message += details
            message += "\n"
        return message

    def on_ok(self):
        self.destroy()


# =============================================================================
# OPENING SCREEN FUNCTION
# =============================================================================
def show_opening_screen():
    config = {}
    win = tk.Tk()
    win.title("Welcome to Monopoly")
    frame = tk.Frame(win, padx=20, pady=20)
    frame.pack()
    tk.Label(frame, text="Welcome to Monopoly!", font=("Arial", 20)).pack(pady=(0, 10))
    game_choice = tk.StringVar(value="new")
    tk.Radiobutton(frame, text="Load Game", variable=game_choice, value="load").pack(
        anchor="w"
    )
    tk.Radiobutton(frame, text="New Game", variable=game_choice, value="new").pack(
        anchor="w"
    )
    human_frame = tk.Frame(frame)
    tk.Label(
        human_frame, text="Number of Human Players (0 for Computer vs Computer):"
    ).pack(side="left")
    human_spin = tk.Spinbox(human_frame, from_=0, to=4, width=5)
    human_spin.pack(side="left")
    human_frame.pack(anchor="w", pady=(10, 0))
    comp_var = tk.IntVar(value=0)
    tk.Checkbutton(
        frame, text="Include one Computer Player (for human games)", variable=comp_var
    ).pack(anchor="w", pady=(5, 0))
    short_game_var = tk.IntVar(value=0)
    tk.Checkbutton(frame, text="Play Short Game Rules", variable=short_game_var).pack(
        anchor="w", pady=(5, 0)
    )

    def on_start():
        config["game_choice"] = game_choice.get()
        config["num_human"] = int(human_spin.get())
        config["include_computer"] = bool(comp_var.get())
        config["short_game"] = bool(short_game_var.get())
        win.destroy()

    tk.Button(frame, text="Start Game", command=on_start).pack(pady=(20, 0))
    win.mainloop()
    return config


# =============================================================================
# MAIN GAME FUNCTION
# =============================================================================
def main():
    config = show_opening_screen()
    global SHORT_GAME
    SHORT_GAME = config.get("short_game", False)
    print(f"Short Game is {SHORT_GAME}")
    if config["game_choice"] == "load":
        players = []
        gui = MonopolyGUI(players)
        gui.load_game()
    else:
        num_human = config["num_human"]
        players = []
        if num_human == 0:
            players.append(Player("Computer 1"))
            players.append(Player("Computer 2"))
        else:
            for i in range(num_human):
                name = simpledialog.askstring(
                    "Player Name", f"Enter name for human player {i+1}:"
                )
                if not name:
                    name = f"Player {i+1}"
                players.append(Player(name))
            if config["include_computer"]:
                players.append(Player("Computer"))
        gui = MonopolyGUI(players)
    gui.mainloop()


if __name__ == "__main__":
    main()
