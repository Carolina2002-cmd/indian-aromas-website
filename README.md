# INDIAN AROMAS by Deepali Saxena: website

A colorful one-page website for the INDIAN AROMAS YouTube channel
(https://www.youtube.com/@indianaromas1404). It's built to bring visitors to the channel,
grow subscriptions and invite collaborations.

## What's on the page

- **Hero thali**: a slowly turning steel plate of real dishes from the channel.
- **Ladoo jar**: subscriber goal (each ladoo = 100 subscribers, goal 10,000).
- **Masala dabba recipe finder**: tap a spice bowl to filter 102 recipes, or search in English or Hindi.
- **From the oven**: bakery display case of cakes, cupcakes and bomboloni.
- **From the kadai**: the 8 most-watched Indian dishes, ranked.
- **Tyohar calendar**: festival recipes; the ones in season are marked automatically.
- **Kya banaun? wheel**: spin to get a random recipe idea.
- **60-second treats**: Shorts strip.
- **Meet Deepali Saxena** and **Collaborate** (idea cards + a form that prepares a ready-to-send message).
- Every "Subscribe" button opens YouTube's subscribe confirmation, and videos play right on the page.

## Put it online (free)

**Netlify Drop (easiest):** go to https://app.netlify.com/drop and drag this whole folder onto the page.
You get a public link in seconds. You can rename it, or connect your own domain later.

**GitHub Pages:** upload the folder to a GitHub repository, then Settings > Pages > deploy from the main branch.

The site is plain HTML, CSS and JavaScript, so any web host works.

## Things to update

All channel details live in `build/data.py`:

- `collab_email`: add Deepali's email to turn on the **Send by email** button in the collaboration form.
  (Until then, the form prepares the message for visitors to copy and send through YouTube.)
- `subscribers`, `subscribers_label`, `videos`: update as the channel grows. The ladoo jar fills automatically.
- `VIDEOS` and `SHORTS`: add new uploads (video ID, views, English title, Hindi title, category, festivals).
  Thumbnails go in `assets/img/videos/<id>.jpg` (640×360) or `assets/img/shorts/<id>.jpg` (360×640).

Then rebuild:

```bash
python3 build/build.py
```

## Notes

- Food photos are the channel's own YouTube thumbnails (collected November 10, 2026).
- Fonts: Yatra One, Mukta and Kalam (SIL Open Font License), self-hosted. Icons: Lucide (ISC license).
- Tested: no accessibility errors (axe-core, WCAG 2.2 AA), works at phone widths down to 320 px,
  keyboard friendly, and respects "reduce motion" settings.
