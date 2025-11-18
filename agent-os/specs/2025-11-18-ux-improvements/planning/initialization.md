# Requested UX improvements.

1. Add counts of available matches to the filter drop-down on the Contacts page.
   E.g.  "All Stages (15)".  If it's easy, count the matching search results, not
   the matching entries in the whole list.

   Now, the data in the Dashboard is fully included in the Contacts page.
   * Login ==> go directly to the Contacts page.
   * Remove the Dashboard.

   Apply the same change for the Filter by Type in the Activity Timeline

2. Goal: Allow attaching files directly when creating an activity with "Add Activity".
   Complexity challenge: This may open up our design for stale uploads or stale
   draft activities that need to be tracked (with additional data base columns) and
   handled (automatic cleanup).  WE DON'T ALLOW COMPLEXITY IN SimpleCRM.

   Solution: Empty activities are fully permitted (like empty documents in Google
   Docs).  All activity records are owned by the user.  He can create them.  He
   can see them.  He can remove them as he wants.  No automation is required.

   Technical: We can create the activity id when the user clicks "New Activity".
   (Note: Add Activity => New Activity: consistent with "New Contact").  Always
   say "Update activity", never "Create Activity" as the activity already exists.

   Default value for activity: Note.  There is no "Select type" option.

3. Show the Pipeline Stage in the timeline -- stage changes are part of an activity.
   * Add a pipeline stage column to the activity data base table (use the correct
     technical names according to the database model).
   * The current pipeline stage of a contact is the stage shown in the last
     activity for this contact in the data base table -- or "Lead" when there are
     no activities.
   * New activities take the stage from the previous activity -- but this can be
     changed.
   * In the timeline list, show the pipeline stage with a badge **when it differs
     from the previous stage**: a change happened in this activity.
   * Show the current badge also next to the name of the contact.
   * Remove the change-stage type form from the contact info tab.

4. Passive Contacts.  Add stages "Qualified Out", "Lost Proposal", "Work Completed"
   and "Archived" to the options of Pipeline Stages:
   * Create two tabs to select contacts:
     * Active (with count) -- Lead, Qualified, Proposal, Client
     * Passive (with count) -- Qualified Out, Lost Proposal, Work Completed, Archived.
   * Thus, passive clients are not visible when we work in the active clients tab.
   * Separate the passive options from the active options with a line in the
     dropdown for status change (to be created in item (3)).

5. Equal space: Use most of the screen width and divide the space equally between the
   Contacts list on the left and the Timeline/Contact info list on the right.

6. Show info from contact.
   * Under the contact name in the right side part (above the timeline/contact info
     tabs): Add the title and the company name -- linked to the website.
