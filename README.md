# Initial Feature Goals and Functionality
Throughout the years, the 5eFC community has been known to be one of the most complex and in-depth D&D servers most of us has ever seen. Because of this, a Discord bot that could be designed to assist users in managing the various features that this server has would be something nothing short of extraodinary. Character management, matchmaking, and server interactions in a streamlined and automated way would not only make our lives easier, but also lower the bar for those who are new to the game itself.

And as for me, being a very much newbie developer and someone who has never done anything in this scale... It feels like an amazing project to really sink my teeth into and use as an excuse to learn programming in a way that is both fun and engaging. All while potentially being able to help people, my friends, and my digital D&D family.

## Goals
RefBot aims to provide a seamless experience for users managing character data and participating in server activities. Key objectives include:
- Automating the process of character roster setup and updates.
- Offering efficient tools for selecting and modifying active characters.
- Enabling intuitive matchmaking between players based on character attributes.
- Providing comprehensive guidance through an interactive help system.

Will all of these work? Will I implement everything? No clue. Probably not. But the sky is the limit and my wings are ready to fly.

## **Envisioned Features**

### **1. Bot Initialization**
Simple stuff. When the RefBot goes online, it announces its availability by sending a message to the system messages channel. For example, the bot might greet users with:

> "Hello World of Evershade! RefBot is now online."

This ensures that users are aware of its functionality and ready to engage with the bot.

### **2. Roster Setup Command (`RosterSetup`)**
The meat and potatoes of the 5eFC Ref Bot system. This command allows for users to register their characters and keep track of them in a way that allows them for easier matchmaking and better handling of information within the server.

When invoked, the bot may:

- **Begin by checking if the user is new or old:**
  - If the user is new, the bot:
    - Sends a welcome message.
    - Adds the user to a list of active members.
    - And requests essential character details, including:
      - Name(s).
      - Level(s).
      - Resurrection count(s).
      - Active/Inactive
      - And other optional features such as descriptions or image links.
    - Once that's done, the bot would organize this information into a structured database with columns for username, character name, level, resurrections, and description.
    - Then it would confirms the data with the user before saving it.
  - If the user *already exists*, the bot redirects them to the `EditRoster` command, ensuring no that there are no duplicate entries.

### **3. Edit Roster Command (`EditRoster`)**
This command allows users to modify existing character information:

- **For Regular Users:**
  - Displays the user’s current roster, including characters, levels, and resurrection counts. Hopefully it displays them in an interesting manner.
  - Offers options to edit:
    - Name.
    - Level (within a range of 1 to 30).
    - Resurrection count (1 to 99).
    - Downtime Days
  - Every edit updates the master database with the new details.

- **For Staff Users:**
  - Provides administrative control to edit any user’s roster.
  - Ensures all updates are reflected in the master list.

### **4. Active Character Command (`ActiveCharacter`)**
This feature simplifies the process of selecting a primary character for interactions:

- The user specifies a character, and the bot:
  - Verifies the input, suggesting corrections if necessary (e.g., "Did you mean `CharacterName`?").
  - Confirms the selection and sets the character as active.
  - And, hopefully, uses some kind of Avrae integration to switch over to the right character.

### **5. Level Up Command (`LevelUp`)**
This command handles character progression based on their current level and resurrection status:

- **For Level 1 to 19 Characters:**
  - Simply increases the level count.

- **For Level 30 Characters:**
  - Offers a choice between:
    - Epic Resurrection: Resets level to 21 and increments the resurrection count.
    - Full Resurrection: Resets level to 1 and increments the resurrection count.

- **For Level 20 Characters:**
  - Checks resurrection availability:
    - If available, prompts the user for a full resurrection (level resets to 1, resurrections increment).
    - If not, progresses the character to level 21.

- The bot confirms all updates with a summary message.

### **6. Matchmaking Command (`Matchmaking`)**
This feature pairs characters for activities or combat based on their attributes:

- **Matchmaking Process:**
  - Notifies the user that matchmaking is in progress.
  - Checks if the active character is already in matchmaking mode:
    - If yes, prompts the user to wait.
    - If no, activates matchmaking for the character, using their level and a resurrection-based bonus to calculate a fighting range.

- **Finding Matches:**
  - Filters characters from the master list within the fighting range.
  - Avoids repeated users.
  - Posts a list of potential matches, including character descriptions.
  - Users can opt into fights via interactive buttons.
  - Assigns a referee to oversee the match once participants are confirmed.

### **7. Ref Command (`RefMe`)**
Another ambitious part of the project, where the bot would help the user calculate rewards for the users when a combat occurs. 
- **Managing a fight**
    - Displays options for arena and traps.
    - Begins a timer.
    - Once fight is done, gives 


### **8. Downtime Days Command (`Downtime`)**
This is a simple counter of downtime days. This goes up when doing fights. 
- **Displaying Downtime**
    - Once invoked, it displays the counter of DowntimeDays your characters as a whole have. 
    - Provides options on how to spend it, leading into *downtime activities*
        - You can select a downtime activity, look up the information about each one, and call out a specific roll for you to do. Once done, it'll display the rewards for you. 

### **9. Help Command (`Help`)**
The Help command offers an interactive guide to RefBot’s capabilities. Users can select a command to view detailed explanations, including:

- `RosterSetup`: How to register characters.
- `EditRoster`: Instructions for modifying character details.
- `ActiveCharacter`: Guide to setting a primary character.
- `LevelUp`: Overview of character progression mechanics.
- `Matchmaking`: Steps to find and engage in matches.
- `RefMe`: How to Self-Ref

### **9. New Character Command (`NewChar`)**
This command streamlines the addition of new characters:

- Prompts users for the same details as `RosterSetup`.
- Integrates new entries seamlessly into the existing roster.