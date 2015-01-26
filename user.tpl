<!DOCTYPE html>
<html>
	<head>
		<title>Caius hall - {{user.crsid}}</title>
		<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css" />
		<meta http-equiv="X-UA-Compatible" content="IE=edge" />

		<meta name="application-name" content="Caius hall - {{user.crsid}}" />
		<meta name="msapplication-config" content="{{ get_url('browserconfig', user=user) }}" />
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
							<dd><p>
								% if m.soup:
									{{ m.starter }}
									<span style="margin-left: 1em; display: block">or</span>
									{{m.soup}}
								% else:
									{{ m.starter }}
								% end
							</p></dd>

							<dt>Main</dt>
							<dd><p>
								% if vegetarian:
									<span class="text-muted">{{ m.main }}</span>
									<span style="margin-left: 1em; display: block">or</span>
									{{ m.main_v }}
								% else:
									{{ m.main }}
									<span style="margin-left: 1em; display: block">or</span>
									<span class="text-muted">{{ m.main_v }}</span>
								% end
							</p></dd>

							<dt>Sides</dt>
							<dd><p>{{! '<br />'.join(m.sides) }}</p></dd>

							<dt>Desert</dt>
							<dd><p>{{ m.dessert }}</p></dd>
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

			<div class="alert alert-info">
				<h1>Hello {{ user.crsid }}!</h1>
				<p>Pin this page to your start screen on windows phone 8 to get information about caius hall.</p>
			</div>
		</div>
	</body>
</html>
