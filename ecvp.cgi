#!/usr/bin/perl 
# CGI script to generate tables of contents. 
# Usage: .../contents.cgi?journal=P&volume=32
#  volume=forthcoming generates advance online publications
#  volume missing generates the current volume contects
#  volume

#

use DBI;
use CGI qw(:standard -no_xhtml);

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

$journal='V';
#$volume=secure(param('volume'));
#$iss=secure(param('issue'));
$year=secure(param('year'));
#$pw=param('pw');


%jname= (
 "V" => "Perception ECVP Abstract Supplement",
 "P" => "Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%jid=(
 "P" => "per",
 "A" => "epa",
 "B" => "epb",
 "C" => "epc",
 "D" => "epd"
);


%startyear=(
 "P" => 1972,
 "A" => 1969,
 "B" => 1974,
 "C" => 1983,
 "D" => 1983
);


$volume=$year-1972+1 if $year;


$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";


#$findlastvol=$dbh->prepare("select max(volume) from papers where journal='$journal' and issue not in (SELECT issue FROM issues where online=0 and issues.volume=papers.volume and issues.journal=papers.journal);") || die;
#$findlastvol=$dbh->prepare("select max(volume) from issues where journal='$journal'") || die;
#$findlastvol->execute()||die "Can't execute query\n";
#($maxvol)=$findlastvol->fetchrow();

#$findlastiss=$dbh->prepare("select max(issue) from papers where journal='$journal' and volume=$maxvol;")||die;
#$findlastiss->execute()||die;
#($maxiss)=$findlastiss->fetchrow();


#$year = 1972+$volume-1;


print header(-charset=>'utf-8',
             -expires=>'600',
            );

#$previous_vol=$volume-1;
#$next_vol=$volume+1;

$jscript =<<END;
function formHandler(form){
var URL = document.form.site.options[document.form.site.selectedIndex].value;
window.location.href = URL;
}
var newwindow;
function popitup(url) {
	newwindow=window.open(url,'helpmenu','location=no, status=yes, menubar=no, scrollbars=yes, resizable=yes, navigationbar=yes, width=460');
	if (window.focus) {newwindow.focus()}
	return false;
}
END


#default_dtd('-//W3C//DTD HTML 4.0 Transitional//EN');
print start_html(-style=>"pion.css", -title=>"Perception ECVP $year Abstracts.", -script=>$jscript, -id=>'per', -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');
# print start_html($jname{$journal}." contents vol $volume");




$gif='p_ban.gif';

$j_name=$jname{$journal};


  $banner='<img src="Images/p_ban2.gif" alt="Perception" border=0 class="logo">';
  $button1="<a href=\"P.html\" title=\"View Perception homepage\">Perception homepage</a>";
  $button2='';
  $example='';


#$options_string= "<option value=\"contents.cgi?journal=$journal&amp;volume=forthcoming\">Forthcoming</option> ";
for($i=2011; $i>=1996; $i--){
  $selected='selected' if $i==$year;
#  $opyear=$startyear{$journal}+$i-1;
  $options_string .= "<option value=\"ecvp.cgi?year=$i\" $selected>$i </option>\n";
  $selected='';
}



print <<END;
    
    <div id="header">
      <a href="P.html">$banner</a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
	    <li><a href="search.cgi?journal=P" title="Search all papers">Search</a></li>
	    <li><a href="contents.cgi?journal=P" title="View latest issue">Current&nbsp;issue</a></li>
	    <li><a href="contents.cgi?journal=P&amp;volume=forthcoming$pw_string" title="View advance online publications">Forthcoming</a></li>
	    <li><a href="allvols.cgi?journal=P" title="View all published volumes">All&nbsp;volumes</a></li>
	    <li>$button1</li>
            <li>$button2</li>
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
	<div class="left"><font size=4><i>European Conference on Visual Perception</i> abstracts</font></div>
	<div class="right"><font size=4>ECVP $year</font></div>
      </div>




   <div id="topspace">
	<div class="search">
	<form method=POST action="search.cgi">
         <font size="-1">
<table border=0 cellspacing=2>
<tr>
<td valign=top align=left>
	 Word or phrase:&nbsp;</td>
<td>	  <input type=text name = query size=20 maxlength=50>&nbsp;
</td>
<tr>
<td>	 Author (surname):</td>
<td>	  <input type=text name = authorquery size=20 maxlength=50>&nbsp;
</td><tr>
<td><a href="search.cgi?journal=$journal"><font size="-1">More options</font></a></td>
<td><input type=submit value="Search"></td>
</table>
<!--	  <br>$example-->
	  <input type=hidden name=journal value=V>
          </font>
	</form>
	</div>
	<div class="dropdown"> 

	  <form name="form" action="contents.cgi"><font size="-1">Go to ECVP</font>
	    <select  onChange="javascript:formHandler(this)" name="site" size=1>
            $options_string
	    </select>&nbsp;&nbsp;</form>
        </div> 
            

           
	 
       
      </div>
END


   $sth=$dbh->prepare("SELECT title, papers.paperid, last_name FROM papers, authors where papers.journal='V' and papers.volume=$volume and authors.position=0 and papers.paperid=authors.paperid    ORDER BY last_name;") || die;  # temporarily removed: and issue not in (SELECT issue FROM issues where online=0 and issues.volume=papers.volume and issues.journal=papers.journal)

  
$sth->execute()||die "Cannot execute query\n";
#"

print p, "For full details of past and future conferences, please visit the <a href='http://www.ecvp.org'>ECVP website</a>.\n", p;



print "<table border=0 cellspacing=0 cellpadding=0 width=100%>";
#print "<font size='-1'>";
$rowcount=0;
while (@result=$sth->fetchrow()){
  ($title, $paperid, $last_name)=@result;
  $rowcount++;   
  
  $paperid =~ s/\s*$//; # delete trailing spaces
  
 
  
  $abslink="<a href=\"abstract.cgi?id=$paperid\"><b>$title</b></a>";
  
  #if ($ptype==1 || $ptype==5 || $ptype==6 || $ptype==2 || $ptype==10){print "<div class='ed'>$abslink</div>"}
  #else{
  #  print "<p>$abslink<br>\n"; }   
  #if ($ptype==3||$ptype==8) {
  #  $abstract =~ s/^\s*(<br>|<p>)//;
  #  $abstract =~ s/<br>\s*<br>/<br>/;
  #  print "<div class='ed'>" if $ptype==8;
  #  print "<font size='-1'>$abstract</font>\n"; # make this smaller and indent
  #  print "</div>" if $ptype==8;
  #}  # reviews
     

  #print "<p><a href=\"abstract.cgi?id=$paperid\"><b>$title</b></a> $start_page-$end_page<br>\n";
  
  $au_number=$dbh->prepare("select count(*) from authors where paperid='$paperid'");
  $au_number->execute();
  ($au_num)=$au_number->fetchrow();
  
  $authquery=$dbh->prepare("select first_name, last_name from authors where paperid='$paperid' order by position")||die;
  $authquery->execute()||die;
  $authors="";
  @author=$authquery->fetchrow();
  ($first_name,$last_name)=@author;
  
  $auth_str="$last_name";
  if($au_num==2){
    @author=$authquery->fetchrow();
    ($first_name,$last_name)=@author;
    $auth_str .= " and $last_name";
  }
  elsif ($au_num>2){
    $auth_str .= " et al";
  }
  
  print "<tr><td valign='top'><font size='-1'>$auth_str</font></td><td valign='top' ><font size='-1'>$abslink</font></td></tr>\n";
  
}  
#print '</font>';
print '</table>'; 



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
