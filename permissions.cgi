#!/bin/perl - T
use CGI::Pretty qw/:standard/;
use Mail::SendEasy;

#$email=param('email');
#$email2=param('email2');
#$message=param('message');
#$to=param('to');
#$subject=param('subject');
#$name=param('name');
#$inst=param('inst');
$journ=secure(param('journ'));
#$refer=param('refer');  


              
 @weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

print header;
#default_dtd('-//W3C//DTD HTML 4.0 Transitional//EN');
print start_html(-style=>"pion.css", -title=>$jname{$journal}." Permissions information", -script=>$jscript, -id=>$jid{$journal}, -head=>Link({-rel=>'alternate', -title=>'Pion RSS feed', -href=>"rss.cgi?journal=$journal", -type=>'application/rss+xml'}), -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
#print start_html(-title=>'Contact Pion', -style=>'pion.css');
     

#============= Print journal specific stuff ===========
if($journ eq 'P'){
 print <<END;
<div id="header">
    <a href="index.html"><img src="Images/p_ban2.gif" alt="Perception" class="logo" /></a>

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
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	</ul>
      </div>
    </div>
END
} elsif($journ eq 'X'| $journ eq 'E'| $journ eq 'A'| $journ eq 'B'| $journ eq 'C'| $journ eq 'D') {
 print <<END;
    <div id="header">
      <a href="index.html"><img src="Images/ep_ban.gif" alt="environment and planning" class="logo" /></a>
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
END
}

#================================================

#======= print common html stuff ================

 print <<END;
    <div id="title">
      <font size=4>
	<div class="left">Permissions information</div>
	<div class="center"></div>
	<div class="right"></div>
      </font>
    </div>
     <div class="space"></div>
      <p><b>Republishing an article or extract</b></p>
      <p>In your query please include the following information:
      <p><li>The original article, journal, year, volume, and page numbers. If you are seeking permission to republish a figure or table, please specify the figure or table number and the page on which it appears.</li>

      <li>The name of the book or journal in which the new article will be published, the author or editor, the publisher, and the expected date of publication.</li>
      <p><b>Photocopy permissions</b></p>

      <p>Please supply the following details:
      <p><li>The course name/number.</li>
      <li>The duration of the course.</li>
      <li>The number of students.</li>
      <li>The number of copies required.</li>
      <p><a href="contact.cgi?to=permissions&amp;journ=$journ">Contact permissions department</a> 
    <div class="space"></div>
    <div id="footer">
      <div class="right">Copyright &copy; $thisyear a <a href="http://www.pion.co.uk">Pion</a> publication.</div>

    </div>
END
#================================================
      print end_html; 


#print form, including any error message, and exit
sub printform {
  print h1("Contact <i>$to</i> at Pion") unless $journ;
  
  #print $ENV{'HTTP_REFERER'};
  
  print p,"<font color='red'>Error: $_[0]</font>",p if $_[0];
  
  print <<END;
     <div class="space"></div>
<form action="contact.cgi" method="post">
<input type="hidden" name="to" value="$to"><input type="hidden" name="refer" value="$ENV{'HTTP_REFERER'}">
Please enter your name:<br>
<input type="text" name="name" value="$name"><br>
Institution (if applicable):<br>
<input type="text" name="inst" value="$inst"><br>
Email address (please enter this carefully as we will need it to reply to you):<br>
<input type="text" name="email"><br>
Please enter your email address again for confirmation:<br>
<input type="text" name="email2">
<p>Subject:<br>
<input type="text" name="subject" size=80 value="$subject">
<p>Message:
<br><textarea name="message" cols="80" rows="16" size="5000">$message</textarea>
<p><input type="submit" value="Send message">
</form>
    <div class="space"></div>
    <div id="footer">
      <div class="right">Copyright &copy; $thisyear a <a href="http://www.pion.co.uk">Pion</a> publication.</div>

    </div>
END
  print end_html;
  exit;
}

 sub secure{
  #return only a single block of alphanumerics to prevent SQL hacking, etc 
  my $input=$_[0];
  $input=~s/\W//g; # delete any non-alpha chars
  return $input;
}
