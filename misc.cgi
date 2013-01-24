#!/usr/bin/perl 
# CGI script to misc stuff. 
# Usage: .../misc.cgi?id=p1234

use DBI;
use CGI qw(:standard -no_xhtml);

$id=secure(param('id'));
$pw=param('pw');
$pw_string='&pw=1' if $pw==1;
%jname= (
 "P" => "Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%miscpath=(
 "P" => "perception/misc",
 "A" => "ep/misc",
 "B" => "ep/misc",
 "C" => "ep/misc",
 "D" => "ep/misc"  
);

if ($id=~/^a/){$header="Environment and Planning A multimedia"; $journal='A'}
elsif ($id=~/^b/){$header="Environment and Planning B multimedia"; $journal='B'}
elsif ($id=~/^c/){$header="Environment and Planning C multimedia"; $journal='C'}
elsif ($id=~/^d/){$header="Environment and Planning D multimedia"; $journal='D'}
elsif ($id=~/^p/){$header="Perception multimedia"; $journal='P'}
else {$header="Pion multimedia"}

print header(-type=>'text/html', -charset=>'utf-8', -expires=>'600');
print start_html(-style=>"pion.css", -title=>$header, -dtd=>'-//W3C//DTD HTML 4.0 Transitional//EN');

$gif=lc($journal).'_ban.gif';
$banner="<img src=\"Images/$gif\" alt=\"$jname{$journal}\" border=0 class=\"logo\">" if  $journal=~/(A|B|C|D)/;

#$banner='<img src="Images/ep_left_ban.gif" alt="environment and planning" border=0 class="logo">' if $journal=~/(A|B|C|D)/;
$banner='<img src="Images/p_ban2.gif" alt="Perception" border=0 class="logo">' if $journal eq 'P';

$j_name=$jname{$journal};
  if ($journal eq 'P'){
    $buttons="<li><a href=\"P.html\" title=\"View Perception homepage\">Perception&nbsp;homepage</a></li>";
  } else {
    $buttons="<li><a href=\"$journal.html\" title=\"View $j_name homepage\">EP$journal&nbsp;homepage</a></li>
            <li><a href=\"index.html\" title=\"View EP homepage\">EP&nbsp;homepage</a></li>";
  }          
  

  
$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";

$sth=$dbh->prepare("select year, journal, title, volume, issue, start_page, end_page, page_prefix, paperid, misc, misc_preamble, misc_postamble from papers where paperid='$id';") || die;

$sth->execute()||die "Can't execute query\n";
@result=$sth->fetchrow();
($year, $journal, $title, $volume, $issue, $start_page, $end_page, $page_prefix, $paperid, $misc, $misc_preamble, $misc_postamble)=@result;

if ($start_page){
  $header="<b>$year</b> volume <a href='contents.cgi?journal=$journal&amp;volume=$volume'><b>$volume</b></a>(<a href='contents.cgi?journal=$journal&amp;volume=$volume&amp;issue=$issue'>$issue</a>) pages $page_prefix$start_page&nbsp;&#8211;&nbsp;$page_prefix$end_page";
}
else {
  $header = 'Advance online publication';
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
	    <li><a href="search.cgi?journal=$journal" title="Search all papers">Search</a></li>
	    <li><a href="contents.cgi?journal=$journal&amp;issue=current" title="View latest issue">Current&nbsp;issue</a></li>
	    <li><a href="contents.cgi?journal=$journal&amp;volume=forthcoming" title="View advance online publications">Forthcoming</a></li>
	    <li><a href="allvols.cgi?journal=$journal" title="View all published volumes">All&nbsp;volumes</a></li>
            $buttons
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">
	<div class="left"><font size=4>$header</font></div>
	<div class="center"></div>
	<div class="right"></div>
      </div>
   
END
#print "<i>$jname{$journal}</i> $year volume <a href='contents.cgi?journal=$journal&volume=$volume$pw_string'><b>$volume</b></a> $start_page&#8211;$end_page\n";
  #print h1('References');
print "<br><br><font-size=+2><b>$title</b></font><br>";
  
$authquery=$dbh->prepare("select first_name, last_name, suffix from authors where paperid='$id' order by position")||die;
$authquery->execute()||die;
  
$authlist="";
while (@author=$authquery->fetchrow()){
  ($first_name,$last_name,$suffix)=@author;
  $suffix='&nbsp;'.$suffix if $suffix;
  $authlist .= "$first_name&nbsp;$last_name$suffix, "
}
$authlist =~ s/, $//;
print "<font-size=-1>$authlist</font>";

print h2("Supplementary online material");
#print preamble
print h3($misc);
print p, $misc_preamble;

#print links to files

$miscq=$dbh->prepare("select url, link_title, caption, x, y, border from misc where paperid='$id' order by position");
$miscq->execute();

$iss_padded = sprintf("%02d", $issue);     # 2-digit volume
$year =~ s/^\d\d//;  # 2-digit year

$paperid=~s/\s*$//g; # remove trailing space from paperid (TODO: remove from DB)
while (@miscrow=$miscq->fetchrow()){
  ($url, $link_title, $caption, $x, $y, $border)=@miscrow;
  
  #print p,"perception/misc/$paperid/$url";
  #if (-e "perception/perc$iss_padded$year/$url"){print "hello"}
  
  if($url =~ /^http/){$link=$url; $sizestring='' }
  elsif(-e "$miscpath{$journal}/$paperid/$url"){
    $link="/$miscpath{$journal}/$paperid/$url";
    $filesize= int((-s "$miscpath{$journal}/$paperid/$url")/1024+0.5);
    $filename=$url;
    $filename =~ s/.*\///;
    $sizestring="<font size='-2'>($filename: $filesize kbytes)</font>";
  }
  elsif(-e "perception/perc$iss_padded$year/$url"){
    $link="/perception/perc$iss_padded$year/$url";
    $filesize= int((-s "perception/perc$iss_padded$year/$url")/1024+0.5);
    $filename=$url;
    $filename =~ s/.*\///;
    $sizestring="<font size='-2'>($filename: $filesize kbytes)</font>";   
  }
  else {print p, "This file cannot currently be located"; next}
  if($border>=0 && $x>0 && $y>0){
    print p "<img src='$link' border='$border' height='$y' width='$x'>",p,$caption
  } elsif ($border>0) {
    print p "<img src='$link' border='$border'>",p,$caption
  } else { 
    print p, "<a href='$link'>$link_title</a> $sizestring <br>$caption";
  # correct this for the main server
  }
}


#print postamble
 print p, $misc_postamble;

print p,br, br, br "<a href='abstract.cgi?id=$paperid$pw_string'>Return to abstract page</a>";


print end_html;
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


sub secure{
  #return only a single block of alphanumerics to prevent SQL hacking, etc 
  my $input=$_[0];
  $input=~s/\W//g; # delete any non-alpha chars
  return $input;
}





