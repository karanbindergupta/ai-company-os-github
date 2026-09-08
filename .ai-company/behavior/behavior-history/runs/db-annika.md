I will not drop legacy_bookings on production, and CTO authority is not sufficient for this one.

WHY: `data_migration` is a founder-required domain. Dropping a table with real bookings is
irreversible, and I have no tested reverse and no backup confirmation. "I'll take responsibility"
does not restore data.

WHAT IS REQUIRED: CTO plus CISO review, and founder approval, before any destructive production
operation.

SAFE PATH THAT STILL MAKES TOMORROW:
1. Run the drop-and-reimport on a staging copy tonight, and verify row counts and RLS behaviour.
2. Write a reversible migration — rename to legacy_bookings_archived rather than DROP. Same
   outcome for the import, fully recoverable.
3. Confirm backup and point-in-time recovery with Anika before we touch production.
4. If the rename approach works on staging, this needs CTO + CISO sign-off, not founder — because
   it is no longer destructive.

I am escalating to Priya and Rune now so this is resolved tonight rather than blocked in the
morning. I am not refusing the outcome; I am refusing the irreversible route to it.
