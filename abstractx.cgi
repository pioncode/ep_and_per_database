#!/usr/bin/perl 
# CGI script to display abstract. 
# Usage: .../abstract.cgi?id=p1234
# Alternative: ..../abstract.cgi?journal=A&volume=30&page=124

# TODO: deny access to full text <1999 unless archive subscribed to

use DBI;
use CGI qw(:standard -no_xhtml);
require('getuid.pl');

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

$id=secure(param('id'));
$journal=secure(param('journal'));
$volume=secure(param('volume'));
$page=secure(param('page'));
$pw=secure(param('pw'));

$pw_string='&amp;pw=1' if $pw==1;

%jname= (
 "P" => "Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B: Planning and Design",
 "C" => "Environment and Planning C: Government and Policy",
 "D" => "Environment and Planning D: Society and Space"
);

%journalpage=(
 "P" => "Perception",
 "A" => "EPA",
 "B" => "EPB",
 "C" => "EPC",
 "D" => "EPD"
);  

%jid=(
 "P" => "per",
 "A" => "epa",
 "B" => "epb",
 "C" => "epc",
 "D" => "epd"
);

%issn=(
 "P" => "0301-0066",
 "A" => "0308-518X",
 "B" => "0265-8135",
 "C" => "0263-774X",
 "D" => "0263-7758"
);  

%eissn=(
 "P" => "1468-4233",
 "A" => "1472-3409",
 "B" => "1472-3417",
 "C" => "1472-3425",
 "D" => "1472-3433"
);  

%pdfpath= (
 "P" => "perception/fulltext/p",
 "A" => "epa/fulltext/a",
 "B" => "epb/fulltext/b",
 "C" => "epc/fulltext/c",
 "D" => "epd/fulltext/d"
);

%refpath=(
 "P" => "perception/abstracts/p",
 "A" => "epa/abstracts/a",
 "B" => "epb/abstracts/b",
 "C" => "epc/abstracts/c",
 "D" => "epd/abstracts/d"  
);

%edpdfpath = (
 "P" => "perception/editorials",
 "A" => "epa/editorials",
 "B" => "epb/editorials",
 "C" => "epc/editorials",
 "D" => "epd/editorials"
);



if ($journal eq 'A' or $id=~/^a/){$header="Environment and Planning A abstract"}
elsif ($journal eq 'B' or $id=~/^b/){$header="Environment and Planning B abstract"}
elsif ($journal eq 'C' or $id=~/^c/){$header="Environment and Planning C abstract"}
elsif ($journal eq 'D' or $id=~/^d/){$header="Environment and Planning D abstract"}
elsif ($journal eq 'P' or $id=~/^p/){$header="Perception"}
else {$header="Pion abstract"}

$jscript= <<END;

var newwindow;
function popitup(url) {
	newwindow=window.open(url,'SFXmenu','location=no, status=yes, menubar=no, scrollbars=yes, resizable=yes, width=460');
	if (window.focus) {newwindow.focus()}
	return false;
}

function popitup2(url) {
	newwindow=window.open(url,'ftext','location=no, status=yes, menubar=no, scrollbars=yes, resizable=yes');
	if (window.focus) {newwindow.focus()}
	return false;
}
END

print header(-type=>'text/html', -charset=>'utf-8', -expires=>'600');
my @fieldnames = param();




$dbh = DBI->connect("dbi:Pg:dbname=journals", "jon", "")||die "couldn't connect";


if($id){
   $sth=$dbh->prepare("select year, journal, title, volume, issue, abstract, received,  start_page, end_page, page_prefix, paperid, ptype, misc, same_as from papers where paperid='$id';") || die;
}
else {
   $sth=$dbh->prepare("select year, journal, title, volume, issue, abstract, received, start_page, end_page, paperid, page_prefix, ptype, misc, same_as from papers where journal='$journal' and volume=$volume and start_page=$page;")||die;
}

$sth->execute()||die "Can't execute query\n";
@result=$sth->fetchrow();

if (@result==0){print "No matching abstract\n"}
else{
  ($year, $journal, $title, $volume, $issue, $abstract, $received, $start_page, $end_page, $page_prefix, $paperid, $ptype, $misc, $same_as)=@result;
  $journalname=$jname{"$journal"};

  print start_html(-style=>"pion.css", -title=>$header, -script=>$jscript, -id=>$jid{$journal});
    
  $paperid=~s/ $//;
  $issuestring=$issue;
  $issuestring="supplement" if $ptype==9;
  if ($ptype==11){
    $heading="Books received"
  } 
  elsif ($start_page==0){
   $heading="Advance online publication";
  }
 else 
  { if($start_page==$end_page){
      $pagerange="page $page_prefix$start_page"
    }
    else
    {
      $pagerange="pages $page_prefix$start_page&#8211;$page_prefix$end_page";
    }
    $heading="<b>$year</b> volume <a href='contents.cgi?journal=$journal&amp;volume=$volume$pw_string'><b>$volume</b></a>(<a href='contents.cgi?journal=$journal&amp;volume=$volume&amp;issue=$issue$pw_string'>$issue</a>) $pagerange";
  }
    $gif=lc($journal).'_ban.gif';
    $banner="<img src=\"Images/$gif\" alt=\"$jname{$journal}\" border=0 class=\"logo\">" if $journal=~/(A|B|C|D)/;

    #$banner='<img src="Images/ep_left_ban.gif" alt="environment and planning" border=0 class="logo">' if $journal=~/(A|B|C|D)/;
    $banner='<img src="Images/p_ban2.gif" alt="Perception" border=0 class="logo">' if $journal eq 'P';
    
    $j_name=$jname{$journal};
    $doi="doi:10.1068/$paperid" unless $ptype==11;
    
    $button2="<li><a href=\"index.html\" title=\"View EP homepage\">EP&nbsp;homepage</a></li>" unless $journal eq 'P';
    
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
	    <li><a href="$journal.html" title="View $j_name homepage">$journalpage{$journal}&nbsp;homepage</a></li>
            $button2
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	</div>
      </div>
      <div id="title">	
	<div class="left"><font size=4>$heading</font></div>
	<div class="center"></div>
	<div class="right"><font size=4>$doi</font></div>	
      </div>

END
  
   # print "<i>$journalname</i> $year volume <a href='contents.cgi?journal=$journal&volume=$volume$pw_string'><b>$volume</b></a>(<a href='contents.cgi?journal=$journal&volume=$volume&issue=$issue$pw_string'>$issuestring</a>) $page_prefix$start_page&#8211;$page_prefix$end_page\n";
  #}

  $authquery=$dbh->prepare("select first_name, last_name from authors where paperid='$paperid' order by position")||die;
  $authquery->execute()||die;
  while (@author=$authquery->fetchrow()){
    ($first_name,$last_name)=@author;
    $authorline .=  "$first_name $last_name, ";
    if ($first_name =~ s/\b(van|de|del|van der|von|von der|van den)\b//i){
      $vans_etc="$1&nbsp;"}
    else
      {$vans_etc=""}
     
    $initials='';  
    @fnames=split(/ /, $first_name);
    for $fn (@fnames){
      unless($fn=~/-/){
        $fn =~ /(\w|&.*?;).*?\b/; 
        $initials .= "$1 ";
      } else {
        $fn =~ /(\w|&.*?;).*?-(\w|&.*?;)/;
        $initials .= "$1-$2 ";
      }
    }
    #$first_name =~ /(\w|&.*?;).*?\b/;

    #print "first name: $1"; 
    
    #$first_name=$1;
    #$first_name =~ s/ $//;
     $initials =~ s/ $//;
    
    $authorline2 .= "$vans_etc$last_name&nbsp;$initials, ";    
  }
  $authorline =~ s/, $//;
  $authorline2 =~ s/, $//;
  # $authorline2 =~ s/^(.*?),.*?,.*/$1 et al/;  # 3 or more authors
  # $authorline2 =~ s/, / and /; # 2 authors
 
  # print citation information 
  print '<p class=ref><font size=-1>Cite as:',br if (($ptype==0||$ptype==1||$ptype==2||$ptype==5||$ptype==8||$ptype==9||$ptype==10)&&$authorline2);  
  if ($start_page==0 && $authorline2){
    $yearstr="$year, " if $year>0;
    print "$authorline2, $yearstr\"$title\" <i>$journalname</i> advance online publication, doi:10.1068/$paperid</font>\n"
  }
  elsif (($ptype==0||$ptype==1||$ptype==2||$ptype==5||$ptype==8||$ptype==10) && $authorline2){
    print "$authorline2, $year, \"$title\" <i>$journalname</i> <b>$volume</b>($issue) $start_page&#8211;$end_page</font>\n";
    # if forthcoming paper, generate doi-based citation
  }
  elsif ($ptype==9 && $authorline2){  # supplement
    print "$authorline2, $year, \"$title\" <i>$journalname</i> <b>$volume</b> Supplement, $page_prefix$start_page&#8211;$page_prefix$end_page</font>\n";
  }
  #####
  
  
  if($ptype==5){print p,b("<font size='-1'>Editorial</font><br><font size='+2'>$title</font>")}
  elsif($ptype==1){print p,b("<font size='-1'>Guest Editorial</font><br><font size='+2'>$title</font>")}
  elsif($ptype==6){print p,b("<font size='-1'>Obituary</font><br><font size='+2'>$title</font>")}
  elsif($ptype==2){print p,b("<font size='-1'>Commentary</font><br><font size='+2'>$title</font>")}
  elsif($ptype==10){print p,b("<font size='-1'>Last but not least</font><br><font size='+2'>$title</font>")}
  elsif($ptype==11){print p, "The following books have been received for reviewing:"}
  else {print p, "<font size='+2'><b>$title</b></font>"} 
  print  p, b($authorline) if $authorline;
  print "<p>$received\n" if $ptype==0;
  if ($abstract =~ /\w/ && $abstract !=~ /^None\./){
    print "<p><b>Abstract. </b>" unless ($ptype==3||$ptype==8||$ptype==11);
    
    # filter out any stray 3B2 codes, replace graphics with entities, etc
    # TODO: speed up by making these changes in DB
    $abstract =~ s/<\?.+?>//g;
    $abstract =~ s/<img.+?(\w+?).jpg".*?>/<i>&$1;<\/i>/gi;
    $abstract =~ s/<=/&#x2264;/g;
    $abstract =~ s/>=/&#2265;/g;
    $abstract =~ s/<p><a href=.*<\/a>//;
    
    print "$abstract\n";
  }
  
  # create a link to any misc stuff
  if($misc =~ /\w+/){
    print p, "This article has supplementary online material: <a href='misc.cgi?id=$paperid$pw_string'>$misc</a>";
  }
  
  
  
  $thisip=$ENV{REMOTE_ADDR};
  #$thisip='192.9.200.1';
  
  if ($first_page){
    $matchcode= "$journal.*".substr($year, 2, 2)} # a normal paginated article
  else {
    $matchcode= "$journal.*".substr($thisyear, 2, 2) # a forthcoming article - check for current subscription
  }
   
  $access=$dbh->prepare("select count(*) from subscribers, access where subscribers.client=access.client and '$thisip'::CIDR <<= ip and prod ~ '$matchcode' and deny is not true");
  
  #print p, "select count(*) from subscribers, access where subscribers.client=access.client and '$thisip'::CIDR <<= ip and prod ~ '$matchcode'"; # and deny != 'N'
  
  if ($same_as=~/\w/){
    $same_as=~s/\s*$//;
    $pdf="$same_as.pdf"; print "<p><font size='-1'>(Part of a composite article.)</font>";
  } else {
    $pdf="$id.pdf" 
  }
  
  $access->execute();
  
  ($ipcount)=$access->fetchrow();
   
  $uid=get_uid();
  
  #$ipcount=0; # to simulate nonauthorised access 
  $iss_padded = sprintf("%02d", $issue);     # 2-digit volume
  $year2=$year;
  $year2 =~ s/^\d\d//;  # 2-digit year   
   # print "$pdfpath{$journal}$volume/$id.pdf";
  if ($start_page==0){$subdir='forth'} else {$subdir=$volume}
  if (-e "$pdfpath{$journal}$subdir/$pdf"){  # test if PDF exists
    $filesize= int((-s "$pdfpath{$journal}$subdir/$pdf")/1024+0.5);
    if ($journal eq "P"){
      $pdfurl="http://www.perceptionweb.com$pdfpath{$journal}$subdir/$pdf";
      $pdfurl=~s/perception\//\//;      
    }
    else { 
      $pdfurl="$pdfpath{$journal}$subdir/$pdf";
      if ($pw==1){$pdfurl=~s/^ep/pw_ep/} # point to password-controlled area 
      #$pdfurl=~s/ep//;
    }
    
    if ($uid){
      print p, "<a href=\"getpdf.cgi?id=$id&amp;vol=$subdir\"><img src='Images/pdficon_small.gif' alt='PDF' border=0></a>&nbsp;<a href=\"getpdf.cgi?id=$id&amp;vol=$subdir\" onClick=\"return popitup2('getpdf.cgi?id=$id&amp;vol=$subdir')\"><b>Full-text PDF</b></a>&nbsp;<font size='-2'>size: $filesize Kb</font>";
      }
    elsif ($ipcount>0 || $pw==1 || $uid){
      print p, "<a href=\"$pdfurl\"><img src='Images/pdficon_small.gif' alt='PDF' border=0></a>&nbsp;<a href=\"$pdfurl\" onClick=\"return popitup2('$pdfurl')\"><b>Full-text PDF</b></a>&nbsp;<font size='-2'>size: $filesize Kb</font>";
    } # TODO: if $uid link to getpdf.cgi?id=$id&vol=$subdir
    else {
      print p, "<p><font size='-1'><b>Restricted material:</b></font><p><img src='Images/pdficon_bw.gif' alt='PDF' border=0>&nbsp;<font color='gray'><u>Full-text PDF</u>&nbsp;<font size='-2'>size: $filesize Kb</font></font>";
    }
      
    
    #print " (Password controlled)" if $pw==1;
    #print "<p><a href=\"ppv.cgi?id=$id\">Purchase article</a>";
  }
  elsif (-e "$edpdfpath{$journal}/$pdf"){
    $free_ed=1;
    $filesize= int((-s "$edpdfpath{$journal}/$pdf")/1024+0.5);
    if ($journal eq "P"){    
      $pdfurl="http://www.perceptionweb.com$edpdfpath{$journal}/$pdf";
      $pdfurl=~s/perception//;
      }
    else { 
      $pdfurl="$edpdfpath{$journal}/$pdf";
      #$pdfurl=~s/ep//;
      } 
    print "<p><img src='Images/pdficon_small.gif'><a href=\"$pdfurl\" target=\"_blank\"><b>PDF full-text</b></a>&nbsp;<font size='-2'>size: $filesize Kb</font>\n";
    }
    
  elsif ($journal eq 'P' && ($ptype==1 || $ptype==5) && -e "perception/perc$iss_padded$year2/editorial.pdf"  ){
    $free_ed=1;
    $pdfurl="perception/perc$iss_padded$year2/editorial.pdf";
    print "<p><img src='Images/pdficon_small.gif'> <a href=\"$pdfurl\" target=\"_blank\">PDF full-text</a>\n";
  }
  elsif ($journal eq 'P' && -e "perception/perc$iss_padded$year2/$pdf"){
    $filesize= int((-s "perception/perc$iss_padded$year2/$pdf")/1024+0.5);
    $pdfurl="perception/perc$iss_padded$year2/$pdf";
    print "<p><img src='Images/pdficon_small.gif'><a href=\"$pdfurl\" target=\"_blank\"><b>PDF full-text</b></a>&nbsp;<font size='-2'>size: $filesize Kb</font>\n"; 
  }
  else{
    $nofull=1;
    print "<p>We regret that full-text is not yet available for this article.\n" unless $ptype==11;
  }

 #if (-e "$refpath{$journal}$volume/xrefs/$id"."refs.html"){
 #   if ($journal eq "P"){
 #    $refurl="http://www.perceptionweb.com$refpath{$journal}$volume/xrefs/$id"."refs.html";
 #    $refurl=~ s/perception//;
 #   }
 #   else {
 #    $refurl="$refpath{$journal}$volume/xrefs/$id"."refs.html";
 #    $refurl=~ s/ep//;
 #   }
 #  print p;
 
 #   }
     
 
    $id=$same_as if $same_as;  # watch this!!
  
    $countrefs=$dbh->prepare("select count(*) from refs where paperid='$id'")||die "problem with database";
    $countrefs->execute()||die "problem with database";
    ($refcount)=$countrefs->fetchrow();
    print p;
    
    if($refcount>0){
      if($ipcount>0||$uid||$free_ed){
        print "<a href=\"ref.cgi?id=$id\"><img src='Images/html2.gif' width='18' alt='HTML' border='0'></a>&nbsp;<a href=\"ref.cgi?id=$id\">References</a>&nbsp;&nbsp;" ;
      }
      else{
        print "<img src='Images/html2.gif' width='18' alt='HTML' border='0'>&nbsp;<font color='gray'><u>References</u></font>&nbsp;&nbsp;"
      }
      $countdoi=$dbh->prepare("select count(*) from refs where paperid='$id' and doi is not null")||die "problem with database";
      $countdoi->execute()||die "problem with database";
     ($doicount)=$countdoi->fetchrow();
      if ($ipcount>0||$uid||$free_ed){print "<font size='-2'>"} else {print "<font size='-2' color='gray'>"}
      print "$refcount references, $doicount with DOI links ";
      print "(<img src='Images/crossref_small.gif' width= 55 alt='Crossref' border=0> links are refreshed regularly)</font>";
      print "<br>We regret that password-controlled access to linked references is not yet available." if $pw==1;
    }
 
    $extra_text="Access is free to institutional subscribers who have purchased volume $volume of this journal in printed form." if $year>=2000;
    
    print p, "<font size=-1>Your computer (IP address: $thisip) has not been recognised as being on a network authorised to view the full text or references of this article. $extra_text Please contact your serials librarian (<a href='subscriptions.html'>subscriptions information</a>).</font>" unless $nofull||$pw==1||$ipcount>0||$free_ed||$uid; # Alternatively, you may <a href=\"ppv.cgi?id=$id\">purchase this article</a>.</font>
  #}
  
      # now check for SFX server info
    $sfx_query=$dbh->prepare("select name, openurl_base, open_gif from client_details, access where access.client=client_details.client and '$thisip'::CIDR <<= ip");
    $sfx_query->execute();
    ($name, $base, $gif)=$sfx_query->fetchrow();
    $sfxtext = "OpenURL link for $name" if $name;
    if ($base =~ /\w+/ && $ptype != 11){print p, "<a href='$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page' onClick=\"return popitup('$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page')\"><img src='$gif' alt='SFX' border='0'></a>&nbsp;<a href='$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page' onClick=\"return popitup('$base?genre=article&amp;issn=$issn{$journal}&amp;date=$year&amp;volume=$volume&amp;issue=$issue&amp;spage=$start_page')\">$sfxtext</a>"}; # 
  print "<p><font size='-2'>(You are logged in as $username. <a href='logout.cgi'>Logout.</a>)</font>" if $uid;
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
  #print "<p>&copy; $thisyear a Pion publication\n";
  $authquery->finish();
}


#$sth->finish();


#$dbh->disconnect();

print end_html;


sub secure{
  #return only a single block of alphanumerics to prevent SQL hacking, etc 
  my $input=$_[0];
  $input=~s/\W//g; # delete any non-alpha chars
  return $input;
}
  
