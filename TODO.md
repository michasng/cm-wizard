# TODO

## Must have

- [x] Bypass cloudflare and login.
- [x] Show overview of all wants lists.
- [x] Show wants list, listing cards.
- [x] Find cheapest prices for single cards.
- [x] Consider filters when searching for cards.
- [ ] Determine most promising sellers for each card.
- [x] Search seller for other cards from the wants list.
- [x] Calculate best combination of sellers with reasonable time complexity.
- [ ] Display final results, linking back to Cardmarket.
- [x] Show incomplete results, if calculation is impossible.
- [x] Consider shipping costs.
- [ ] Filter shipments by country.

## Should have

- [ ] Allow optionally saving credentials in a file.
- [ ] Support other cardgames (currently just Yugioh, because I have no experience with other games)
- [ ] Cache prices and offers.  
       Regularly expire the cache and/or allow users to evict it.
- [ ] Save the progress of the wizard (especially in case of failure).  
       It should be transparent how the wizard searched and calculated the best prices.  
       This would also allow for manually searching for ideas for improvements.

## Nice to have

- [ ] Support other languages.
      Easy way: Just translate this application.
      Hard way: Send and parse requests in other languages.
- [ ] Automatically determine user-agent header.  
       Is this possible? Maybe by sending a request from the browser to this app?

## Won't have

- Wants list management. This application is not supposed to replace the cardmarket website itself. Such features are way out of scope.

## Known issues

- [ ] Links to specific products are different from general cards.  
       One difference is the presence or absence of a "version" in some product vs. card IDs, e.g. `/Products/Singles/Metal-Raiders/Time-Wizard-V1-Ultra-Rare` vs. `/Cards/Time-Wizard`, which is handled by RegEx matching and cutting the version from the ID.  
       Then there are also some differences that are less predictable, like `/Products/Singles/.../Dragon-s-Fighting-Spirit-V-2` vs. `/Cards/Dragons-Fighting-Spirit`. This likely stems from the fact that IDs are manually assigned and are not necessarily consistent. Those are handled by fuzzy string matching IDs.  
       This is still an issue until the specific product page for product IDs instead of the general card page.
- [ ] Use pagination to find all offers from a seller on the wants list.
- [ ] Search cards from a specific expansion.  
       The query parameter `idExpansion` of the `/Cards` endpoint is not mapped, so unwanted results could be found. This parameter requires the numerical IDs of expansions, but we only know the abbreviations at this point.
- [x] HTTP error 429 (too many requests) needs to be handled.  
       This occurs when we send many requests to find the best prices. Pause 30 seconds (plus 2 seconds to avoid race conditions). Then retry those failed requests.
- [x] Avoid 429 by limiting requests.  
       Running into 429 repeatedly might eventually be noticed by cardmarket staff, which should be avoided. They likely don't want people scraping their platform, but on the other hand their official shopping wizard does not find the best prices, so this is sadly the only alternative for buying many single cards.
- [x] Navigating back while loading does not interrupt the wizard.  
       This will break the UI and the user gets stuck on the previous page.
- [ ] Variable shipping costs.  
       Shipping costs are currently constant. Instead they should depend on seller and buyer countries.
