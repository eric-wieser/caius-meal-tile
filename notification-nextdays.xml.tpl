% def checkbox(checked):
%     return u'\u2713' if checked else u'\u2718'
% end

% def stringify(data):
%     return u"{cb} {date:%b %d}{more}".format(
%         cb=checkbox(data.hall is not None),
%         date=data.date,
%         more=u" - {}".format(data.hall.type.name) if data.hall else u''
%     )
% end

<tile>
	<visual lang='en-US' version='2'>
		<binding template="TileSquare71x71Image" branding="none">
			<image id="1" src="{{ domain }}{{ get_url('images', path='food-{}.png'.format(status)) }}"/>
		</binding>

		<binding template="TileSquare150x150PeekImageAndText01" branding="name">
			<image id="1" src="{{ domain }}{{ get_url('images', path='food-{}.png'.format(status)) }}"/>
			% for i, data in enumerate(days[:4]):
				<text id="{{i}}">{{stringify(data)}}</text>
			% end
		</binding>

		<binding template="TileWide310x150PeekImage02" branding="name">
			<image id="1" src="{{ domain }}{{ get_url('images', path='food-{}-wide.png'.format(status)) }}"/>
			% for i, data in enumerate(days[:5]):
				<text id="{{i}}">{{stringify(data)}}</text>
			% end
		</binding>
	</visual>
</tile>