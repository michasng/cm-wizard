# TODO

## Must have

- [x] Bypass cloudflare and login
- [x] Show overview of all wants lists
- [x] Show wants list, listing cards
- [x] Find cheapest prices for single cards
- [ ] Consider filters when searching for cards
- [ ] Determine most promising sellers for each card
- [ ] Search seller for other cards from the wants list
- [ ] Calculate best combination of sellers  
       (might be a dynamic programming problem)
- [ ] Display final results, linking back to Cardmarket

## Should have

- [ ] Optionally allow saving credentials in a file
- [ ] Support other cardgames (currently just Yugioh, because I have no experience with other games)

## Nice to have

- [ ] Support other languages
      Easy way: Just translate this application.
      Hard way: Send and parse requests in other languages.
- [ ] Automatically determine user-agent header  
       Is this possible? Maybe by sending a request from the browser to this app?

## Won't have

- Wants list management. This application is not supposed to replace the cardmarket website itself. Such features are way out of scope.

## Known issues

- [ ] Links to specific products are different from general cards.  
       In want to avoid parsing both result pages, which are structurally different, e.g. `/Cards/Time-Wizard` and `/Products/Singles/Metal-Raiders/Time-Wizard-V1-Ultra-Rare`. I need to get the ID differently from the URL (without the "V1-Ultra-Rare" part).
