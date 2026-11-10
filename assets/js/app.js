/* INDIAN AROMAS by Deepali Saxena: page interactions.
   Everything works without JavaScript too (links go straight to YouTube). */
(function () {
	'use strict';
	var CONFIG = window.IA_CONFIG || {};
	var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	var $ = function (sel, root) { return (root || document).querySelector(sel); };
	var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

	/* ---------- Recipe explorer: masala dabba filter, search, show more ---------- */
	var grid = $('#recipe-grid');
	var cards = $$('.recipe-card', grid);
	var katoris = $$('.katori');
	var search = $('#recipe-search');
	var status = $('#explorer-status');
	var empty = $('#recipe-empty');
	var more = $('#show-more');
	var PAGE = window.matchMedia('(max-width: 600px)').matches ? 6 : 12;
	var state = { filter: 'all', q: '', limit: PAGE };

	function applyFilter() {
		var q = state.q.trim().toLowerCase();
		var shown = 0;
		var matches = 0;
		cards.forEach(function (card) {
			var okCat = state.filter === 'all' || card.dataset.cat === state.filter;
			var okQ = !q || card.dataset.search.indexOf(q) !== -1;
			var match = okCat && okQ;
			card.hidden = !match;
			if (match) {
				matches++;
				var clip = matches > state.limit;
				card.classList.toggle('is-clipped', clip);
				if (!clip) shown++;
			}
		});
		empty.hidden = matches !== 0;
		more.hidden = matches <= state.limit;
		more.textContent = 'Show more recipes (' + (matches - shown) + ' more)';
		var label = state.filter === 'all' ? 'all recipes' : (CONFIG.categories[state.filter] || state.filter).toLowerCase();
		status.textContent = matches === 0 ? 'No recipes found.' :
			'Showing ' + shown + ' of ' + matches + ' ' + (q ? 'results for “' + state.q.trim() + '” in ' : '') + label + ', most watched first.';
	}

	katoris.forEach(function (btn) {
		btn.addEventListener('click', function () {
			state.filter = btn.dataset.filter;
			state.limit = PAGE;
			katoris.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
			applyFilter();
		});
	});
	if (search) {
		search.addEventListener('input', function () { state.q = search.value; state.limit = PAGE; applyFilter(); });
	}
	if (more) {
		more.addEventListener('click', function () {
			var firstHidden = $('.recipe-card.is-clipped:not([hidden])', grid);
			state.limit += PAGE;
			applyFilter();
			if (firstHidden) { var link = $('a', firstHidden); if (link) link.focus({ preventScroll: false }); }
		});
	}
	if (grid) applyFilter();

	/* ---------- Video player dialog ---------- */
	var player = $('#player');
	var frame = $('#player-frame');
	var playerTitle = $('#player-title');
	var playerYt = $('#player-yt');
	var lastTrigger = null;

	function openPlayer(id, kind, title, url, trigger) {
		if (!player || typeof player.showModal !== 'function') { window.open(url, '_blank', 'noopener'); return; }
		lastTrigger = trigger || null;
		playerTitle.textContent = title;
		playerYt.href = url;
		player.classList.toggle('player--short', kind === 'short');
		frame.innerHTML = '';
		var iframe = document.createElement('iframe');
		iframe.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0&modestbranding=1';
		iframe.title = title + ' (YouTube video)';
		iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
		iframe.allowFullscreen = true;
		iframe.loading = 'lazy';
		frame.appendChild(iframe);
		player.showModal();
		$('#player-close').focus();
	}
	function closePlayer() { if (player.open) player.close(); }
	if (player) {
		player.addEventListener('close', function () {
			frame.innerHTML = '';
			if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus();
		});
		player.addEventListener('click', function (e) { if (e.target === player) closePlayer(); });
		$('#player-close').addEventListener('click', closePlayer);
	}
	document.addEventListener('click', function (e) {
		var a = e.target.closest('[data-play]');
		if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
		e.preventDefault();
		openPlayer(a.dataset.play, a.dataset.kind, a.dataset.title || a.textContent.trim(), a.href || a.dataset.url, a);
	});

	/* ---------- Festival calendar: mark what's in season now ---------- */
	var month = new Date().getMonth() + 1;
	var strip = $('#fest-strip');
	var firstNow = null;
	$$('.fest').forEach(function (f) {
		var months = (f.dataset.months || '').split(',').map(Number);
		if (months.indexOf(month) !== -1) {
			f.classList.add('is-now');
			$('.fest__now', f).hidden = false;
			if (!firstNow) firstNow = f;
		}
	});
	if (strip && firstNow) {
		strip.scrollLeft = Math.max(0, firstNow.offsetLeft - strip.offsetLeft - 8);
	}

	/* ---------- Kya banaun? Spin the tadka wheel ---------- */
	var spinBtn = $('#spin-btn');
	var wheel = $('#wheel-spin');
	var result = $('#spin-result');
	var cats = katoris.filter(function (k) { return k.dataset.filter !== 'all'; }).map(function (k) { return k.dataset.filter; });
	var turned = 0;
	var spinning = false;

	function showPick(cat) {
		var pool = cards.filter(function (c) { return c.dataset.cat === cat; });
		var card = pool[Math.floor(Math.random() * pool.length)];
		var link = $('.recipe-card__title a', card);
		var img = $('img', card).getAttribute('src');
		var hi = $('.recipe-card__hi', card).textContent;
		result.innerHTML = '';
		var wrap = document.createElement('div');
		wrap.className = 'pick';
		wrap.innerHTML = '<img alt="" width="640" height="360"><div><p class="pick__cat"></p><p class="pick__title"></p><p class="pick__hi" lang="hi"></p>' +
			'<div class="btn-row"><button type="button" class="btn btn--pink">Play recipe</button>' +
			'<a class="btn btn--outline" target="_blank" rel="noopener">Watch on YouTube</a></div></div>';
		$('img', wrap).src = img;
		$('.pick__cat', wrap).textContent = 'The wheel says: ' + CONFIG.categories[cat];
		$('.pick__title', wrap).textContent = link.dataset.title;
		$('.pick__hi', wrap).textContent = hi;
		var play = $('button', wrap);
		play.dataset.play = link.dataset.play;
		play.dataset.kind = link.dataset.kind;
		play.dataset.title = link.dataset.title;
		play.dataset.url = link.href;
		var yt = $('a', wrap);
		yt.href = link.href;
		result.appendChild(wrap);
	}

	if (spinBtn && wheel) {
		spinBtn.addEventListener('click', function () {
			if (spinning) return;
			spinning = true;
			spinBtn.setAttribute('aria-disabled', 'true');
			var idx = Math.floor(Math.random() * cats.length);
			var seg = 360 / cats.length;
			var target = 360 - (idx * seg + seg / 2);
			var extra = 360 * (4 + Math.floor(Math.random() * 2));
			var current = turned % 360;
			turned += extra + ((target - current + 360) % 360);
			wheel.style.transform = 'rotate(' + turned + 'deg)';
			var done = function () {
				if (!spinning) return;
				spinning = false;
				spinBtn.removeAttribute('aria-disabled');
				showPick(cats[idx]);
			};
			if (reduceMotion) { done(); } else {
				wheel.addEventListener('transitionend', done, { once: true });
				setTimeout(done, 4000);
			}
		});
	}

	/* ---------- Share ---------- */
	$$('[data-share]').forEach(function (btn) {
		btn.addEventListener('click', function () {
			var data = { title: 'INDIAN AROMAS by Deepali Saxena', text: 'Vegetarian Indian recipes, festival sweets and cakes. Subscribe on YouTube!', url: CONFIG.channel };
			if (navigator.share) { navigator.share(data).catch(function () {}); return; }
			var label = $('span', btn);
			var old = label.textContent;
			var ok = function () { label.textContent = 'Link copied!'; setTimeout(function () { label.textContent = old; }, 2200); };
			if (navigator.clipboard) { navigator.clipboard.writeText(CONFIG.channel).then(ok, function () { window.open(CONFIG.channel, '_blank', 'noopener'); }); }
			else { window.open(CONFIG.channel, '_blank', 'noopener'); }
		});
	});

	/* ---------- Collaboration form ---------- */
	var form = $('#collab-form');
	if (form) {
		var err = $('#form-error');
		var done = $('#form-done');
		var msg = $('#f-message');
		form.addEventListener('submit', function (e) {
			e.preventDefault();
			var fields = ['f-name', 'f-org', 'f-email', 'f-idea'].map(function (id) { return document.getElementById(id); });
			var bad = fields.filter(function (f) { return !f.value.trim() || (f.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value.trim())); });
			fields.forEach(function (f) { f.setAttribute('aria-invalid', String(bad.indexOf(f) !== -1)); });
			if (bad.length) {
				var names = bad.map(function (f) { return $('label[for="' + f.id + '"]').textContent.toLowerCase(); });
				err.textContent = 'Please add ' + names.join(', ') + (bad.some(function (f) { return f.type === 'email' && f.value.trim(); }) ? ' (check the email address)' : '') + '.';
				err.hidden = false;
				bad[0].focus();
				return;
			}
			err.hidden = true;
			var v = function (id) { return document.getElementById(id).value.trim(); };
			var subject = 'Collaboration idea: ' + v('f-type') + ' with ' + v('f-org');
			var body = 'Namaste Deepali ji,\n\n' +
				'I am ' + v('f-name') + ' from ' + v('f-org') + '. I would love to collaborate with INDIAN AROMAS.\n\n' +
				'Kind of collaboration: ' + v('f-type') + '\n' +
				'Timing: ' + v('f-when') + '\n\n' +
				'My idea:\n' + v('f-idea') + '\n\n' +
				'You can reach me at ' + v('f-email') + '.\n\nThank you!\n' + v('f-name');
			msg.value = 'Subject: ' + subject + '\n\n' + body;
			var send = $('#send-email');
			var help = $('#done-help');
			if (CONFIG.email) {
				send.href = 'mailto:' + CONFIG.email + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
				send.hidden = false;
				help.textContent = 'Send it by email, or copy it if your email app doesn’t open.';
			} else {
				send.hidden = true;
				help.textContent = 'Copy your message, then send it to INDIAN AROMAS through the channel on YouTube.';
			}
			done.hidden = false;
			done.focus();
		});
		$('#copy-message').addEventListener('click', function () {
			var st = $('#copy-status');
			var fallback = function () { msg.focus(); msg.select(); st.textContent = 'Message selected. Press Ctrl+C (or ⌘+C) to copy.'; };
			if (navigator.clipboard) {
				navigator.clipboard.writeText(msg.value).then(function () { st.textContent = 'Copied! Paste it into your message.'; }, fallback);
			} else { fallback(); }
		});
	}

	/* ---------- Floating subscribe button: hide where a big subscribe button is already on screen ---------- */
	var floatSub = $('#float-sub');
	if (floatSub && 'IntersectionObserver' in window) {
		var visible = new Set();
		var io = new IntersectionObserver(function (entries) {
			entries.forEach(function (en) { if (en.isIntersecting) visible.add(en.target); else visible.delete(en.target); });
			floatSub.classList.toggle('is-hidden', visible.size > 0);
		}, { threshold: 0.15 });
		$$('.hero, .goal, .bell, .site-footer').forEach(function (el) { io.observe(el); });
	}

	/* ---------- Ladoos drop into the jar when it scrolls into view ---------- */
	var goal = $('.goal');
	if (goal && !reduceMotion && 'IntersectionObserver' in window) {
		var rect = goal.getBoundingClientRect();
		if (rect.top > window.innerHeight) {
			var gio = new IntersectionObserver(function (entries) {
				if (entries[0].isIntersecting) { goal.classList.add('is-in'); gio.disconnect(); }
			}, { threshold: 0.35 });
			gio.observe(goal);
		}
	}
})();
