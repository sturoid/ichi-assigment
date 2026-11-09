# Glossary ("Words you'll need")

Source: the challenge README's terms table, pasted by the user on 2026-11-08. These are the challenge author's plain-language explanations. **They are not building-code text.** Code definitions such as IBC Section 202 live in `tests/fixtures/code/`.

| Term | What it means here |
|---|---|
| Drawing set, sheet | Architects submit drawings as a stack of large pages called sheets, numbered like A0.1 or A6.1. Each sheet holds one kind of thing, like a floor plan, an elevation or a table, and the whole stack is the drawing set. |
| Cover sheet | The first sheet in the set (A0.1 here). It has the project name, the list of sheets, the codes that apply, and the code analysis. |
| Code analysis | A table on the cover sheet where the architect sums up the building: what it's used for, how it's built, how tall it is, and the limits they looked up. Everything in it is the architect's claim. File: fixtures/project/code-analysis.html. |
| Window schedule | A table on its own sheet (A6.1 here) that lists every window with its ID, room, size, type and a few flags. File: fixtures/project/window-schedule.html. |
| Type mark | A short code (A, B, C...) that points to a detail drawing of that window type somewhere else in the set. In the fixture schedule it's the second of the two TYPE columns. It doesn't tell you how the window opens; the first TYPE column does. |
| IBC | The International Building Code. We're using the 2018 edition. |
| Occupancy group | A code for what the building is used for. R-3 is a house, B is an office, and A is assembly (theaters, restaurants and so on). A numbered group like R-3 goes in the Table 504.3 row for its letter, R, unless the table gives the numbered group its own row, which it does for H and I. |
| Construction type | A label for how fire-resistant the structure is, from I-A (concrete and steel high-rises) down to V-B (wood-frame houses). |
| Sprinklered | Whether the building has fire sprinklers, and to which standard. NFPA 13 is full commercial coverage, NFPA 13R is a lighter residential standard, and NFPA 13D is the lightest one, meant for houses. The better the sprinkler system, the taller the code lets you build. |
| Grade plane | The average ground level around the building. Building height is measured from here. |
| Story, floor, level | These mean the same thing on drawings. The first floor is the first story above grade plane, and so on up. The code analysis says how room numbers map to floors. |
| Finished floor (F.F.) | The top of the finished floor. F.F. EL. 101.0' is its elevation, its height relative to a reference point on the site. |
| Sleeping room | A room people sleep in. Anything named as a bedroom (BEDROOM, BED, BDRM, GUEST BED and so on) counts. People do sometimes sleep in dens, offices and lofts, so if a room name leaves you unsure, say so in the report instead of quietly guessing. |
| Egress / emergency escape and rescue opening | A window someone can climb out of in a fire, and a firefighter can climb in through. Most residential buildings need one in every bedroom. The schedule marks these in its EGRESS column. |
| Nominal size | The size of the window unit as ordered, including the frame. This is what the schedule gives you. |
| Net clear opening | The actual hole you can climb through with the window open. It's always smaller than the nominal size, by an amount that depends on the frame and how the window opens, and it's what the code regulates. |
| Head height | Height from the floor to the top of the window. The schedule gives this. |
| Sill height | Height from the floor to the bottom of the window. The code limits it, but the schedule doesn't list it. |
| Casement / single hung / slider / fixed / awning | How the window opens. A casement swings out like a door, so nearly the whole thing opens. A single hung slides up, so only the bottom half opens. A slider slides sideways and opens about half its width. An awning is hinged at the top and swings out at the bottom. A fixed window doesn't open. On schedules, CASM'T is casement and S.H. is single hung, and L.H. and R.H. (left hand and right hand) just say which side the hinge is on. |
| Feet and inches | 2' - 6" is 2 feet 6 inches, or 30 inches. The spacing varies, so 2'-6" means the same thing. |
