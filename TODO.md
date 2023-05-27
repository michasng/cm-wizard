# TODO

## Must have

- [x] Bypass cloudflare and login
- [x] Show overview of all wants lists
- [x] Show wants list, listing cards
- [x] Find cheapest prices for single cards
- [x] Consider filters when searching for cards
- [ ] Determine most promising sellers for each card
- [x] Search seller for other cards from the wants list
- [x] Calculate best combination of sellers  
       (might be a dynamic programming problem)
- [ ] Display final results, linking back to Cardmarket
- [ ] Consider shipping costs
- [ ] Filter shipments by country

## Should have

- [ ] Allow optionally saving credentials in a file
- [ ] Support other cardgames (currently just Yugioh, because I have no experience with other games)
- [ ] Cache prices and offers.  
       Regularly expire the cache and/or allow users to evict it.
- [ ] Save the progress of the wizard (especially in case of failure).  
       It should be transparent how the wizard searched and calculated the best prices.  
       This would also allow for manually searching for ideas for improvements.

## Nice to have

- [ ] Support other languages
      Easy way: Just translate this application.
      Hard way: Send and parse requests in other languages.
- [ ] Automatically determine user-agent header  
       Is this possible? Maybe by sending a request from the browser to this app?

## Won't have

- Wants list management. This application is not supposed to replace the cardmarket website itself. Such features are way out of scope.

## Known issues

- [ ] The results page is not scrollable yet.
- [x] Links to specific products are different from general cards.  
       One difference is the presence or absence of a "version" in some product vs. card IDs, e.g. `/Products/Singles/Metal-Raiders/Time-Wizard-V1-Ultra-Rare` vs. `/Cards/Time-Wizard`, which is handled by RegEx matching and cutting the version from the ID.  
       Then there are also some differences that are less predictable, like `/Products/Singles/.../Dragon-s-Fighting-Spirit-V-2` vs. `/Cards/Dragons-Fighting-Spirit`. This likely stems from the fact that IDs are manually assigned and are not necessarily consistent. Those are handled by fuzzy string matching IDs.
- [ ] Search cards from a specific expansion.  
       The query parameter `idExpansion` of the `/Cards` endpoint is not mapped, so unwanted results could be found. This parameter requires the numerical IDs of expansions, but we only know the abbreviations at this point.
- [x] HTTP error 429 (too many requests) needs to be handled.  
       This occurs when we send many requests to find the best prices. Likely need to pause between requests every so often when this error occurs. Also need to retry those failed requests.
- [ ] Navigating back while loading does not interrupt the wizard.  
       This will break the UI and the user gets stuck on the previous page.
