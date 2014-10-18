<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
  <msapplication>
    <tile>
      <square70x70logo src="/images/smalltile.png"/>
      <square150x150logo src="/images/mediumtile.png"/>
      <wide310x150logo src="/images/widetile.png"/>
      <TileColor>#7C431C</TileColor>
    </tile>
    <notification>
      <polling-uri src="{{ get_url('nt-today', user=user) }}"/>
      <polling-uri2 src="{{ get_url('nt-nextdays', user=user) }}"/>
      <frequency>30</frequency>
    </notification>
  </msapplication>
</browserconfig>
