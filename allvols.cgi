#!/bin/perl
# past.cgi?journal=A    generates page of links to all volumes

use DBI;
use CGI qw(:standard -no_xhtml);

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

$journal=secure(param('journal'));
$pw=param('pw');
if ($pw==1){
  $pw_string="\&pw=1";
}

%jname= (
 "P" => "Perception",
 "H" => "High Temperatures &#8211; High Pressures",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%startyear=(
 "H" => 1969,
 "P" => 1972,
 "A" => 1969,
 "B" => 1974,
 "C" => 1983,
 "D" => 1983
);

%jid=(
 "P" => "per",
 "A" => "epa",
 "B" => "epb",
 "C" => "epc",
 "D" => "epd"
);

$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";

$findlastvol=$dbh->prepare("select max(volume) from issues where journal='$journal';") || die;
$findlastvol->execute()||die "Can't execute query\n";
($maxvol)=$findlastvol->fetchrow();

#$vols=$dbh->prepare("select DISTINCT volume, year from papers where journal='$journal' and issue not in (SELECT issue FROM issues where online=0 and issues.volume=papers.volume and issues.journal=papers.journal) order by volume desc;") || die;

$vols=$dbh->prepare("select DISTINCT volume from issues where journal='$journal' order by volume desc");
$vols->execute()||die "Can't execute query\n";

$lines_per_column=int($maxvol/4 + (2 + (-1)**($maxvol+1) )/2);

#$pullup=-1.3*$lines_per_column.'em';

$jscript =<<END;
function formHandler(form){
var URL = document.form.site.options[document.form.site.selectedIndex].value;
window.location.href = URL;
}
END

$style= <<END;
 ul {
  margin: 0;
  padding: 0;
  list-style-type: none;

}

li {
  margin: 0;
  padding: 0;
  line-height: 1.5em;
}

#columns {
 /* background-color: #16FF16; */
 position: relative;
 top: 0em;
 width: 100%;
}
#column1 {
 position: relative; 
 top: 0em;
 left: 3em;
 width: 10em
}
#column2 {
 position: absolute; 
 top: 0em;
 left: 13em;
 width: 10em
}
#column3 {
 position: absolute; 
 top: 0em;
 left: 23em;
 width: 10em
}

#column4 {
 position: absolute; 
 top: 0em;
 left: 33em;
 width: 10em
}


END

$gif=lc($journal).'_ban.gif';
$banner="<img src=\"Images/$gif\" alt=\"$jname{$journal}\" border=0 class=\"logo\">" if $journal=~/(A|B|C|D)/;
$banner='<img src="Images/p_ban2.gif" alt="Perception" border=0 class="logo">' if $journal eq 'P';
print header(-charset=>'utf-8');
print start_html(-style=>{-src=>'pion.css', -code=>$style},
                 -title=>$jname{$journal}." volumes",
                 -script=>$jscript, -id=>$jid{$journal}, 
                 -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
$j_name=$jname{$journal};   

if ($journal eq 'P'){
  $buttons="<li><a href=\"P.html\" title=\"View Perception homepage\">Perception&nbsp;homepage</a></li>";
  $example="";
} else {
  $buttons= <<END;
<li><a href="$journal.html" title="View $j_name homepage">EP$journal&nbsp;homepage</a></li>
            <li><a href="index.html" title="View EP homepage">EP&nbsp;homepage</a></li>
END
  $example='Example: (town or urban) planning';
}
                              
print <<END;  
    <div id="header">
      <a href="$journal.html">$banner</a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="search.cgi?journal=$journal$pw_string" title="Search all papers">Search</a></li>
	    <li><a href="contents.cgi?journal=$journal&amp;issue=current$pw_string" title="View latest issue">Current&nbsp;issue</a></li>
	    <li><a href="contents.cgi?journal=$journal&amp;volume=forthcoming$pw_string" title="View advance online publications">Forthcoming</a></li>
	    <li><a href="allvols.cgi?journal=$journal$pw_string" title="View all published volumes">All&nbsp;volumes</a></li>
	    $buttons
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
	<font size=4>
	<div class="left">All volumes</div>
	<div class="center"></div>
	<div class="right"></div>
	</font>
      </div>
      <div id="topspace">
	<div class="search">
	<form method=POST action="search.cgi" align="right">
	  <input type=hidden name=journal value=$journal>
         <table border=0 cellspacing=2>
        <tr>
        <td valign=top align=left>
	 Search abstracts:&nbsp;</td>
        <td align=left>	  <input type=text name = query size=20 maxlength=50>&nbsp;
</td>
<tr>
<td>	 (and/or) author:</td>
<td align=left>	  <input type=text name = authorquery size=20 maxlength=50>&nbsp;
</td><tr>
<td><a href="search.cgi?journal=$journal"><font size="-1">More options</font></a></td>
<td align=right><input type=submit value="Search">&nbsp;</td>
</table>
	
	</form>
	</div>
      </div>

END

print h2($jname{$journal});


# divide number of volumes by 4. Round up. This is the number of lines per column.



#print "lines per column: $lines_per_column";

$count=0;
print '<div id="columns"><ul><div id="column1">';
$thiscol=1;
while(@row=$vols->fetchrow){
 $column=int($count++/$lines_per_column+1);
 if($column != $thiscol){print "</div><div id=\"column$column\">"; $thiscol=$column}
 ($volume)=@row;
 $year=$startyear{$journal}+$volume-1;
  #print "column=$column:  ";
 if ($maxvol==$volume){print "<li><a href='contents.cgi?journal=$journal&amp;volume=$volume$pw_string'><b>Current</b> $volume ($year)</a></li>\n"}
 else {print "<li><a href='contents.cgi?journal=$journal&amp;volume=$volume$pw_string'>Volume $volume ($year)</a></li>\n"} 
}
print "</div></ul></div>";

print <<END;
   <div class="space"></div>
      <div id="footer">
	<div class="left">
	  <i>$jname{$journal}</i>
      </div>
	<div class="right">
	  Copyright &copy;&nbsp;$thisyear a <a href="http://www.pion.co.uk">Pion</a> publication
	</div>
      </div>
    </div>
END
print end_html;

sub secure{
  #return only a single block of alphanumerics to prevent SQL hacking, etc 
  my $input=$_[0];
  $input=~s/\W//g; # delete any non-alpha chars
  return $input;
}

