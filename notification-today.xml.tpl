<tile>
	<visual lang='en-US' version='2'>
		<binding template="TileSquare71x71Image" branding="none">
			<image id="1" src="{{ domain }}{{ get_url('images', path='food-{}.png?v=2'.format(status)) }}"/>
		</binding>

		<binding template="TileSquare150x150PeekImageAndText01" branding="name">
			<image id="1" src="{{ domain }}{{ get_url('images', path='food-{}.png?v=2'.format(status)) }}"/>
			<text id="1">{{ "{:%B %d} - {}".format(hall.date, hall.type.name) }}</text>
			<text id="2">{{ hall.menu.starter }}</text>
			<text id="3">{{ hall.menu.main }}</text>
			<text id="4">{{ hall.menu.dessert }}</text>
		</binding>

		<binding template="TileWide310x150PeekImage02" branding="name">
			<image id="1" src="{{ domain }}{{ get_url('images', path='food-{}-wide.png?v=2'.format(status)) }}"/>
			% m = hall.menu
			<text id="1">{{ "{:%B %d} - {}".format(hall.date, hall.type.name) }}</text>
			<text id="2">{{ "{} or {}".format(m.starter, m.soup) if m.soup else m.starter}}</text>
			<text id="3">{{ m.main }}</text>
			<text id="4">{{ m.sides }}</text>
			<text id="5">{{ m.dessert }}</text>
		</binding>
	</visual>
</tile>