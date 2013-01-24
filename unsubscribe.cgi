#!/usr/bin/perl -T
# email alert service: process activation

%jname= (
 "P" => "Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%jname= (
 "P" => "Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%bannername= (
 "P" => "p_ban2.gif",
 "A" => "a_ban.gif",
 "B" => "b_ban.gif",
 "C" => "c_ban.gif",
 "D" => "d_ban.gif"
);

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;
use CGI::Pretty qw/:standard/;
use DBI;

$db= DBI->connect("dbi:Pg:dbname=emailalert;host=localhost;port=5432", "jon", "") || failmsg("We're sorry, an error has occurred, please try again later");

$id=param('i');
$number=param('n');

# trap any non-numeric input (prevent SQL hacking)
exit unless ($id =~ /^\d+$/ && $number =~ /^\d+$/);

print header, start_html(-title=>"Pion email alerting service", -style=>'pion.css', -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');

$sth=$db->prepare("select random, journal from emailaddresses where id=$id");
$sth->execute();
($random,  $journal)=$sth->fetchrow();
$journal =~s/\s*//g;

if($journal eq 'P'){
 print <<END;
<div id="header">
    <a href="P.html"><img src="Images/p_ban2.gif" alt="Perception" class="logo" /></a>

    <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
  </div>
  <div id="total">
    <div id="top-buttons">
      <div class="topnavigation">
	<ul>
	  <li><a href="search.cgi?journal=P." title="Search all papers">Search</a></li>
	  <li><a href="contents.cgi?journal=P&issue=current" title="View latest issue">Current&nbsp;issue</a></li>
	  <li><a href="contents.cgi?journal=P" title="View latest volume">Current&nbsp;volume</a></li>
	  <li><a href="contents.cgi?journal=P&volume=forthcoming" title="View forthcoming papers">Forthcoming</a></li>
	  <li><a href="allvols.cgi?journal=P" title="View all published volumes">All&nbsp;volumes</a></li>
	  <li><a href="index.html" title="Go to Perception homepage">Perception&nbsp;homepage</a></li>
          <li><a href="ECVP.html" title="ECVP abstracts">ECVP</a></li>
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	</ul>
      </div>
    </div>
    <div id="title">
      <font size=4>
	<div class="left">Email alerting service registration</div>
	<div class="center"></div>
	<div class="right"></div>

      </font>
    </div>
END
} elsif($journal eq 'X'| $journal eq 'E'| $journal eq 'A'| $journal eq 'B'| $journal eq 'C'| $journal eq 'D') {
 print <<END;
    <div id="header">
      <a href="$journal.html"><img src="Images/$bannername{$journal}" alt="$jname{$journal}" class="logo" /></a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="A.html" title="Go to Environment and Planning A homepage">EPA&nbsp;homepage</a></li>
	    <li><a href="B.html" title="Go to Environment and Planning B homepage">EPB&nbsp;homepage</a></li>
	    <li><a href="C.html" title="Go to Environment and Planning C homepage">EPC&nbsp;homepage</a></li>
	    <li><a href="D.html" title="Go to Environment and Planning D homepage">EPD&nbsp;homepage</a></li>
	    <li><a href="index.html" title="Go to Environment and Planning homepage">EP&nbsp;homepage</a></li>
	    <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
      <font size=4>
	<div class="left">Email alerting service registration</div>
	<div class="center"></div>
	<div class="right"></div>

      </font>
    </div>
END
} else {
 print <<END;
   <div id="header">
      <a href="http://www.pion.co.uk"><img src="Images/pion_new2.gif" alt="Pion" class="logo"/></a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="librarians.html" title="Information for librarians">For&nbsp;librarians</a></li>
	    <li><a href="contacts.html" title="Contact Pion">Pion&nbsp;contacts</a></li>
	    <li><a href="index.html" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
      <font size=4>
	<div class="left">Email alerting service registration</div>
	<div class="center"></div>
	<div class="right"></div>
      </font>
    </div>
END
}

$footer=<<END;
       <div class="space"></div>
    <div id="footer">
	<div class="right">Copyright &copy; $thisyear a <a href="http://www.pion.co.uk">Pion</a> publication.</div>
    </div>
END

if ($random == $number){
  $db->do("delete from emailaddresses where id=$id") || failmsg("We're sorry, an error has occurred, please try again later");
  print p, "You have successfully unsubscribed from the <i>$jname{$journal}</i> email alerting list.";
}

else{
  unless ($random){print p, "You have already unsubscribed from this service."}
  else {print p, "Invalid input"}

}


print $footer, end_html;

sub failmsg {
  print p, $_[0], end_html;
  exit;
}
