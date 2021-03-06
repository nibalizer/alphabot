Trailbot: A snarky IRC bot to keep track of trips for #afk

Abstract:

Trailbot is a pet project of mine for #afk, a channel for people to plan
awesome trips, events, etc., that all take place away from their keyboards.
With trailbot, users can add trips to a list, view the upcoming trips, 
use shared google docs that are generated on the fly to organize the trips,
and after all is said and done complete the trip for viewing in a past log.
Support for other features, including editing and testing, is described
below under Current Features.

Current Features:

	- cmds.py and docs.py can be edited and dynamically rebuilt into the running
	  trailbot without disconnecting from the IRC server. This is possible with
	  the '@reload' command and Twisted's rebuild.py module in client.py.

	- All commands for trailbot to interact with the trip logs or give help are
	  prefixed with '@'.

	- All commands can be used on test logs, as to not screw with the actual
	  trips that #afk is planning. This is done with '@test <cmd> [args]' instead
	  of '@cmd [args]'.

	- Most responses trailbot will give have been pulled out to voices.py, which
	  allows for dynamic updating and random selection. The command specific
	  confirmations remain in client.py and cmds.py.

	- Bot commands include:
	  
		- @add <trip description> : The <trip description> is first appended with
		  a shortened google doc link that is generated from template.txt, then
		  written to the open trip log in sorted order.

		- @remove <keywords> : <keywords> can contain one or more words that 
		  match a trip currently in the open trip log. The match is also done
		  case insensitive, then removes the match from the open trip log. In
		  the case of multiple matches, only the first match is removed.

		- @edit <keywords> s/<old>/<new>/ : <keywords> is treated the same as in
		  @remove to match a specific trip, then whatever is in <old> with 
		  whatever is in <new>. <old> and <new> can both be any number of words,
		  but <old> is a case sensitive match. If <old> or <new> happens to
		  contain '/', trailbot can deal with it as long as it is escaped by
		  using '\/' instead. Any edits done to the trips through trailbot will
		  be consistent across the google doc.

		- @comp <keywords> : <keywords> again can be a case insensitive match of
		  any number of words to match a specific trip. This command moves the
		  matching trip from the open log to the corresponding past log, which
		  can be viewed with @past. Whenever a trip is moved, the appended link
		  to the google doc is removed and the google doc itself is trashed.

		- @photos <keywords> <link> : Like the previous commands, <keywords> is
		  used to find a matching trip to alter. The <link> is appended to the
		  trip that is found in the past log. The link will also be shortened,
		  like the google doc addition in @add.

		- @help [command] : With no arguments, it displays a list of implemented
		  commands. With a specific command argument, it'll display a specific
		  reply corresponded to the command's usage and description.

		- @next : This returns the next dated trip to the channel. Simple, and
		  it makes more sense than the previous implementation of @list, which
		  did the same thing and sent the rest in a private message.

		- @show <keys> : This simply pulls a trip matching <keys> to the channel
		  for everyone to see. It first searches the current log, then it goes
		  to the corresponding past log. This should encourage use of @photos
		  since folks can show past trips to others in the channel.

		- @list : When given, a private message will be sent to the user with 
		  all of the currently planned trips. The trips will be sorted based on
		  date, with the undated trips appended.

		- @past : Similar to @list, the past log is returned to the user in a
		  private message. The first entry in the returned list is sent to the
		  channel, which is just a status message telling the user to check
		  their private message for the past trips.

		- @source : A reply is sent to the channel giving a github link to the
		  trailbot code along with an invitation to join #trailbot, the dev
		  channel for trailbot.

	- Hooks to IRC actions:

		- On joining the channel, trailbot announces it is back.

		- When a user is kicked, trailbot scolds the kicker for being harsh.

		- When a user joins the channel, trailbot greets the user appropriately.
		  Note that once you've been greeted, trailbot remembers your nick so
		  you won't be greeted again.

		- When a user leaves the channel, trailbot mourns the loss.

		- When trailbot receives good/bad karma, trailbot responds appropriately.

Ideas/Hopes for Future:

	- All items are subject to change, depend highly on suggestions from others
	  in the channel, and are in no preference or order.

	- @map <place> : Not sure yet, but I'd like to intergrate some sort of
	  mapping feature into trailbot. Whether it's a link to a map, textual
	  directions, or something completely different is yet to be seen.

	- Pull common, repetitive logic out of commands/methods and replace with
	  more generic method calls.

	- Manage time nicks have been gone, so if a user has been gone for a given
	  period of time trailbot will greet them. Also keep a separate nick list
	  each channel.

	- Update google doc trip description when @edit is done.

	- Increase overall snarky attitude, find more ways to comment on things.

Dependencies:

	- twisted : All the IRC bits and module reloading is handled by twisted.

	- gdata : Google Documents List Data API, used for the doc generation and 
	  deletion when users add and remove trips.

	- tinyurl : TinyUrl interface for shortening the doc links before appending
	  them to the newly added trip.

Contribute:

	- Feel free to fork, suggest new features, try to break trailbot, or even
	  by me food/beer.
