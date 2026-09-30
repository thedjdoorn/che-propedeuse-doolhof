<script lang="ts">
	import maze from '$lib/maze.json';

	type Dir = 'up' | 'down' | 'left' | 'right';
	const { cells, h, v, fills, labels } = maze;
	const START = { r: 3, c: 19 };
	const DELTA: Record<Dir, [number, number]> = { up: [-1, 0], down: [1, 0], left: [0, -1], right: [0, 1] };
	const BACK: Record<Dir, Dir> = { up: 'down', down: 'up', left: 'right', right: 'left' };
	const STEP_MS = 45;

	const isCell = (r: number, c: number) => cells[r]?.[c] !== undefined && cells[r][c] !== '.';
	const wall = (r: number, c: number, d: Dir) =>
		d === 'up' ? h[r][c] : d === 'down' ? h[r + 1][c] : d === 'left' ? v[r][c] : v[r][c + 1];
	const open = (r: number, c: number, d: Dir) => wall(r, c, d) === '0';

	// Static drawing: one path per fill colour / wall thickness.
	const rgb = (f: string) => {
		const p = f.split(' ').map((x) => Math.round(+x * 255));
		return `rgb(${p.length === 1 ? [p[0], p[0], p[0]] : p})`;
	};
	const cellPaths = fills.map((f, i) => ({
		fill: rgb(f),
		d: cells.flatMap((row, r) => [...row].map((k, c) => (k === String(i) ? `M${c} ${r}h1v1h-1z` : ''))).join('')
	}));
	const wallPath = (k: string) =>
		h.flatMap((row, r) => [...row].map((x, c) => (x === k ? `M${c} ${r}h1` : ''))).join('') +
		v.flatMap((row, r) => [...row].map((x, c) => (x === k ? `M${c} ${r}v1` : ''))).join('');
	const thin = wallPath('1');
	const thick = wallPath('2');

	let pos = $state({ ...START });
	let trail = $state([`${START.c + 0.5},${START.r + 0.5}`]);
	let startedAt = $state(0);
	let now = $state(0);
	let finished = $state(false);
	let timer: ReturnType<typeof setInterval> | undefined;
	let raf = 0;

	const elapsed = $derived(startedAt ? now - startedAt : 0);
	const fmt = (ms: number) => {
		const s = Math.floor(ms / 1000);
		return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}.${Math.floor((ms % 1000) / 100)}`;
	};

	function tickClock() {
		now = performance.now();
		if (!finished) raf = requestAnimationFrame(tickClock);
	}

	// Slide in a direction, following corridor bends, until a junction, dead end or the exit.
	function go(d: Dir) {
		if (finished || !open(pos.r, pos.c, d)) return;
		if (!startedAt) {
			startedAt = now = performance.now();
			tickClock();
		}
		clearInterval(timer);
		let dir = d;
		timer = setInterval(() => {
			const [dr, dc] = DELTA[dir];
			const r = pos.r + dr, c = pos.c + dc;
			pos = { r, c };
			trail.push(`${c + 0.5},${r + 0.5}`);
			if (!isCell(r, c)) {
				// The only opening in the outer wall is the main entrance.
				finished = true;
				now = performance.now();
				return clearInterval(timer);
			}
			const exits = (Object.keys(DELTA) as Dir[]).filter((x) => x !== BACK[dir] && open(r, c, x));
			if (exits.length === 1) dir = exits[0];
			else clearInterval(timer);
		}, STEP_MS);
	}

	function reset() {
		clearInterval(timer);
		cancelAnimationFrame(raf);
		pos = { ...START };
		trail = [`${START.c + 0.5},${START.r + 0.5}`];
		startedAt = now = 0;
		finished = false;
	}

	const KEYS: Record<string, Dir> = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right' };
	function onkeydown(e: KeyboardEvent) {
		const d = KEYS[e.key];
		if (!d) return;
		e.preventDefault();
		go(d);
	}

	let touch: { x: number; y: number } | null = null;
	function onpointerdown(e: PointerEvent) {
		touch = { x: e.clientX, y: e.clientY };
	}
	function onpointerup(e: PointerEvent) {
		if (!touch) return;
		const dx = e.clientX - touch.x, dy = e.clientY - touch.y;
		touch = null;
		if (Math.max(Math.abs(dx), Math.abs(dy)) < 20) return;
		go(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : dy > 0 ? 'down' : 'up');
	}
</script>

<svelte:window {onkeydown} />
<svelte:head><title>CHE Doolhof</title></svelte:head>

<header>
	<span class="time" aria-live="off">{fmt(elapsed)}</span>
	<button onclick={reset}>Opnieuw</button>
</header>

<main {onpointerdown} {onpointerup} onpointercancel={() => (touch = null)}>
	<svg viewBox="-0.5 -1.5 45 57" role="img" aria-label="Doolhof van ICT-lokaal naar de hoofdingang">
		{#each cellPaths as p}<path d={p.d} fill={p.fill} />{/each}
		<path d={thin} stroke="#708aa3" stroke-width="0.059" stroke-linecap="square" />
		<path d={thick} stroke="#004070" stroke-width="0.174" stroke-linecap="square" />
		<line x1="7.957" y1="45.257" x2="9.106" y2="45.909" stroke="#004070" stroke-width="0.134" stroke-dasharray="0.214 0.241" />
		<circle cx="10.04" cy="46.85" r="1.34" fill="#fff" stroke="#004070" stroke-width="0.107" />
		{#each labels as [x, y, size, text, green]}
			<text {x} {y} font-size={size} fill={green ? '#2fac66' : '#004070'}>{text}</text>
		{/each}
		<polyline points={trail.join(' ')} fill="none" stroke="#2fac66" stroke-width="0.18" stroke-opacity="0.6" stroke-linejoin="round" />
		<circle class="player" r="0.38" fill="#2fac66" style:transform="translate({pos.c + 0.5}px, {pos.r + 0.5}px)" />
	</svg>

	{#if finished}
		<div class="done">
			<p>Buiten in <strong>{fmt(elapsed)}</strong></p>
			<button onclick={reset}>Nog een keer</button>
		</div>
	{:else if !startedAt}
		<p class="hint">Veeg of gebruik de pijltjestoetsen. De tijd start bij je eerste stap.</p>
	{/if}
</main>

<style>
	:global(html) {
		color-scheme: light;
	}
	:global(body) {
		margin: 0;
		background: #fff;
		color: #004070;
		font-family: system-ui, sans-serif;
		overflow: hidden;
	}
	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 16px;
		height: 44px;
		box-sizing: border-box;
	}
	.time {
		font-size: 1.5rem;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
	}
	button {
		font: inherit;
		font-weight: 600;
		color: #fff;
		background: #004070;
		border: 0;
		border-radius: 6px;
		padding: 6px 14px;
		cursor: pointer;
	}
	main {
		position: relative;
		height: calc(100dvh - 44px);
		touch-action: none;
		user-select: none;
	}
	svg {
		display: block;
		width: 100%;
		height: 100%;
	}
	text {
		font-weight: 700;
	}
	.player {
		transition: transform 45ms linear;
	}
	.hint,
	.done {
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
		margin: 0;
		background: #fff;
		border: 2px solid #004070;
		border-radius: 8px;
		padding: 10px 16px;
		text-align: center;
	}
	.hint {
		bottom: 16px;
		font-size: 0.9rem;
		width: max-content;
		max-width: calc(100% - 32px);
		box-sizing: border-box;
	}
	.done {
		top: 40%;
		font-size: 1.25rem;
	}
	.done p {
		margin: 0 0 10px;
	}
</style>
