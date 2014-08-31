<!DOCTYPE html>
<html>
	<head>
		<title>Caius meal stuff</title>
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
		<h1>Hello {{user}}!</h1>
		<p>Pin this page to your start screen to get information about caius hall.</p>
		<p>For medium and wide tiles, the reverse side shows the menu for today.</p>
		<h2>First hall booked</h2>
		<div class="screen">
			<img src="images/food-booked.png" class="small"/>
			<img src="images/food-booked-wide.png" class="wide"/>
			<img src="images/food-booked.png" class="tiny"/>
		</div>
		<h2>Formal hall booked</h2>
		<div class="screen">
			<img src="images/food-booked-formal.png" class="small"/>
			<img src="images/food-booked-formal-wide.png" class="wide"/>
			<img src="images/food-booked-formal.png" class="tiny"/>
		</div>
		<h2>No hall booked</h2>
		<div class="screen">
			<img src="images/food-closed.png" class="small"/>
			<img src="images/food-closed-wide.png" class="wide"/>
			<img src="images/food-closed.png" class="tiny"/>
		</div>
		<h2>Default tile</h2>
		<div class="screen">
			<img src="images/mediumtile.png" class="small"/>
			<img src="images/widetile.png" class="wide"/>
			<img src="images/smalltile.png" class="tiny"/>
		</div>
	</body>
</html>