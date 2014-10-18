<!DOCTYPE html>
<html>
	<head>
		<title>Caius hall - {{user}}</title>
		<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css" />
		<meta http-equiv="X-UA-Compatible" content="IE=edge" />

		<meta name="application-name" content="Caius hall - {{user}}" />
		<meta name="msapplication-config" content="/{{user}}/browserconfig.xml" />
	</head>
	<style>
		body {
			font-family: Segoe WP;
		}
		h1, h2 {
			font-family: Segoe WP Semilight;
		}
		img {
			display: block;
			margin: 5px;
			float: left;
			background: #7C431C;
		}
		.wide {
			width: 310px;
			height: 150px;
		}
		.small {
			width: 150px;
			height: 150px;
		}
		.tiny {
			width: 70px;
			height: 70px;
		}
		.screen {
			background: black;
			width:480px;
			padding: 5px;
			overflow: hidden;
		}
		.sep {
			clear: both;

		}
	</style>
	<body role="application">
		<div class="container">
			<div class="alert alert-info">
				<h1>Hello {{user}}!</h1>
				<p>Pin this page to your start screen on windows phone 8 to get information about caius hall.</p>
			</div>


			% m = hall.menu
			<div class="row">
				<div class="col-xs-3">
					<img class="img-responsive" src="{{ get_url('images', path='food-{}.png?v=2'.format(status)) }}"/>
				</div>
				<div class="col-xs-9">
					<h2>
						{{ "{:%B %d} - {}".format(hall.date, hall.type.name) }}
					</h2>
					% if m:
						<dl class="dl-horizontal">
							% if m.bread:
								<dt>Bread</dt>
								<dd>{{ m.bread }}</dd>
							% end

							<dt>Starter</dt>
							<dd>{{! "{}<br>or<br>{}".format(m.starter, m.soup) if m.soup else m.starter}}</dd>

							<dt>Main</dt>
							% if vegetarian:
								<dd class="text-muted">{{ m.main }}</dd>
								<dd>{{ m.main_v }}</dd>
							% else:
								<dd>{{ m.main }}</dd>
								<dd class="text-muted">{{ m.main_v }}</dd>
							% end

							<dt>Sides</dt>
							<dd>{{! '<br />'.join(m.sides) }}</dd>

							<dt>Desert</dt>
							<dd>{{ m.dessert }}</dd>
						</dl>
					% else:
						<p>menu not published</p>
					% end
					<a href="{{ hall.url }}">Full site</a>
					<form action="{{ hall.url }}" method="post">
						<input type="hidden" name='edit'/>
						<button type="submit">Book / edit</button>
					</form>
					<form action="{{ hall.url }}" method="post">
						<input type="hidden" name='delete'/>
						<button type="submit">Delete</button>
					</form>
				</div>
			</div>
		</div>
	</body>
</html>
