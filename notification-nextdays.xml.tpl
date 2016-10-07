<%
def checkbox(checked):
    return u'\u2713' if checked else u'\u2718'
end

def stringify(data):
    return u"{cb} {date:%b %d}{more}".format(
        cb=checkbox(data.is_booked),
        date=data.date,
        more=u" - {}".format(data.hall.type.name) if data.is_booked else u''
    )
end
%>
<tile>
	<visual lang='en-US' version='2'>
		<binding template="TileSmall">
			<image placement="background" src="{{ get_abs_url('images', path='food-{}.png?v=2'.format(status)) }}"/>
		</binding>

		<binding template="TileMedium" branding="name">
			% for data in days:
				<text hint-style="body">{{stringify(data)}}</text>
			% end
		</binding>

		<binding template="TileWide" branding="name">
			% for data in days:
				<text hint-style="body">{{stringify(data)}}</text>
			% end
		</binding>

		<binding template="TileSquare71x71Image" branding="none">
			<image id="1" src="{{ get_abs_url('images', path='food-{}.png?v=2'.format(status)) }}"/>
		</binding>

		<binding template="TileSquare150x150Text01" branding="name">
			% for i, data in enumerate(days[:4]):
				<text id="{{i}}">{{stringify(data)}}</text>
			% end
		</binding>

		<binding template="TileWide310x150Text01" branding="name">
			% for i, data in enumerate(days[:5]):
				<text id="{{i}}">{{stringify(data)}}</text>
			% end
		</binding>
	</visual>
</tile>