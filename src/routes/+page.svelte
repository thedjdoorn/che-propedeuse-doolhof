<script lang="ts">
	import Maze from '$lib/Maze.svelte';
	import maze from '$lib/maze2.json';
</script>

<Maze
	{maze}
	START={{ r: 49, c: 25 }}
	viewBox="-0.5 -1.5 51 57"
	exit={{ line: [7.957, 19.257, 9.106, 19.909], circle: [10.04, 20.85] }}
/>
