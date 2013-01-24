#!/usr/bin/perl 

# Usage: .../search.cgi?journal=P&query='fdfdfd'
# TODO: alternatives (most optional): ....?journal=ACD&query='fff'&year=2000&volume=20&issue=3&page=123&type=A

# type = A (authors) or S (subject, ie abstract)
# journal=X => all EP journals


use DBI;
use CGI qw(:standard :html3 -no_xhtml);
use Text::Unidecode;
use HTML::Entities;
use HTML::Template;

#Load the Google search function
my $gtemplate = HTML::Template->new(filename => 'google_search.tmpl');

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

$journal=secure(param('journal'));
$query=param('query');
$authorquery=param('authorquery');
$pw=param('pw');
#$year=param('year'); # search from this year
$year=secure(param('volume'));
$issue=secure(param('issue'));
$page=secure(param('page'));
$type=param('type'); # A or S
$results_page=param('respage');
$query_orig=$query;

$pw_hidden='<INPUT TYPE="hidden" name="pw" value=1>' if $pw==1;
$limit=25;

if($results_page == undef){$offset=0}
else{$offset=$limit*$results_page}

%jname= (
 "V" => "Perception ECVP Abstract Supplement",
 "P" => "Perception",
 "A" => "Environment and Planning A",
 "B" => "Environment and Planning B",
 "C" => "Environment and Planning C",
 "D" => "Environment and Planning D",
 "H" => "High Temperatures - High pressures"
);


exit if $journal =~ '[^A-D,P,X,V,H]';
$journal='ABCD' if $journal eq 'X';
$journalstring=$journal;
$journalstring=~s/(.)/'$1',/g;
$journalstring=~s/,$//;

$searchstring="journal in ($journalstring)";
$searchstring .= " and year::int2>=$year" if $year =~ /^\d+$/;
$searchstring .= " and volume=$volume" if $volume =~ /^\d+$/;
$searchstring .= " and issue=$issue" if $issue =~ /^\d+$/;
$searchstring .= " and page=$page" if $page =~ /^\d+$/;

#print $searchstring;

#if($abstract && $authors){
 # $query="select title, issue, start_page, end_page, paperid, headline(abstract, q), rank(vectors, q) from papers, to_tsquery($query_quoted) as q where vectors @@ q and journal='$journal' order by rank(vectors, q) DESC";
  
 


$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "")||die "couldn't connect";

$dbh->do("select set_curcfg('default')");

$jscript =
"function formHandler(form){
      var URL = document.form.site.options[document.form.site.selectedIndex].value;
      window.location.href = URL;
      
      
      if (mainform.volume.value >= 1969) {
      YDiv.style.visibility='visible';
      }
      
      three=/^\d{4}\$/;
      function validate() {
      if (mainform.volume.value <= 1968 || mainform.volume.value >= 2007) {
      alert('Please enter a year within the range 1969 - 2006 or select \"Search all years\" ');
      return false;
      } else return true;
      }
      function cleanslate() { 
      mainform.volume.value =\"\";
      }
}
function no() {
      YDiv.style.visibility='hidden';
      mainform.volume.value =\"1969\";
}
function yes() {
      YDiv.style.visibility='visible';
      mainform.volume.value =\"\";
      mainform.volume.focus();
}
";

print header;
print start_html(-title=>$jname{$journal}." search", -style=>'pion.css', -script=>$jscript, -dtd=>'-//IETF//DTD HTML//EN');

unless ($query_orig =~ /\w+/ || $authorquery =~ /\w+/){
  if ($journal =~ /(A|B|C|D|X)/ || $journal eq ''){
    $heading='Search <i>E&amp;P</i> titles, abstracts, authors';
    $banner='<img src="Images/ep_left_ban.gif" alt="environment and planning" border=0 class="logo">' 
  }
  elsif ($journal =~ /(P|V)/){
    $heading="Search <i>Perception</i> titles, abstracts, authors";
    $banner='<img src="Images/p_ban2.gif" alt="Perception" border=0 class="logo">'
  } elsif ($journal =~ /H/) {
    $heading='Search <i>HTHP</i> titles, abstracts, authors';
    $banner='<img src="Images/h_ban2.gif" alt="High Temperatures &#8211; High Pressures" border=0 class="logo">' 
  } else {$heading = "Pion journal search"; }
 
  if ($journal =~ /(P|V)/){
    if ($journal eq 'P') {$checked_P='checked'} else {$checked_V='checked'}
    print <<END;
      <div id="header">
      <a href="index.html">$banner</a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
          <li><a href="P.html" title="Go to Perception homepage">Perception&nbsp;homepage</a></li>
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
	  </ul>
	</div>
      </div>
      <div id="title">
	<font size=4>
	<div class="left">$heading</div>
	<div class="center"></div>
	<div class="right"></div>
	</font>
      </div>
       <!-- <p>Perception abstracts are available from 1972.<p><br> -->
      <form name="mainform"  onsubmit="return validate();" method=get >
	<p> 

	 
      Words or phrase:<br>
      &nbsp;&nbsp;<input type=text name = query size=32 maxlength=80> <br>
      Author (surname or initial followed by surname):<br>
      &nbsp;&nbsp;<input type=text name = authorquery size=32 maxlength=80> <br>   

	<input type=radio name = journal $checked_P value ="P">&nbsp;Perception&nbsp;&nbsp;&nbsp;        
	<input type=radio name = journal $checked_V value = "V">&nbsp;ECVP&nbsp;&nbsp;&nbsp;
        <input type=radio name = journal value = "PV">&nbsp;Both&nbsp;&nbsp;&nbsp;
      <p>
      <INPUT TYPE="Radio" NAME="volume1" CHECKED onClick="no()">All years
	  <INPUT TYPE="Radio" NAME="volume1" UNCHECKED onclick="yes()">From a specific year to present
      <div id="YDiv" style="visibility:hidden">
	<label for="Year">
	  <p>Enter year to search from: &nbsp;&nbsp;<INPUT TYPE="TEXT" VALUE="1969" NAME="volume" SIZE=4 MAXLENGTH=4><p>
	</label>
      </div> 
      <p>
      $pw_hidden
      <p><INPUT TYPE="SUBMIT" action="search.cgi">
      <INPUT TYPE="RESET" >
    </FORM>
<p><p><font size=2><b>Advanced use</b> A space between keywords has the effect of an 'and' operator, and will produce results containing all the supplied keywords. The operator 'OR' between two keywords will match one or both keywords. Parentheses may be used for more complex searches. Search will attempt to match all standard variants of a word (plurals, gerunds etc). Double quotation marks around an expression will perform an exact search for that expression. All searches are case insensitive. Examples: 
      <br><b>change blindness</b> will match documents containing both 'change' and 'blindness'. <br><b>change or blindness</b> will match documents containing either 'change' or 'blindness' (or variants such as 'blind'). <br><b>(change or colour) blindness</b> will match documents containing either 'change' and 'blindness', or 'colour' and 'blindness'.
      <br> <b>"change blindness"</b> (ie within double quotes) will match only the string 'change blindness'.</font>
      <p>
END
print      $gtemplate->output;
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
  } elsif ($journal eq 'H'){
    print <<END;
      <div id="header">
      <a href="index.html">$banner</a>
      <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
    </div>
    <div id="total">
      <div id="top-buttons">
	<div class="topnavigation">
	  <ul>
          <li><a href="H.html" title="Go to High Temperatures - High Pressures homepage">HTHP&nbsp;homepage</a></li>
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>	
	  </ul>
	</div>
      </div>
      <div id="title">
	<font size=4>
	<div class="left">$heading</div>
	<div class="center"></div>
	<div class="right"></div>
	</font>
      </div>
       <!-- <p>Perception abstracts are available from 1972.<p><br> -->
      <form name="mainform"  onsubmit="return validate();" method=get >
	<p> 

	 
      Words or phrase:<br>
      &nbsp;&nbsp;<input type=text name = query size=32 maxlength=80> <br>
      Author (surname or initial followed by surname):<br>
      &nbsp;&nbsp;<input type=text name = authorquery size=32 maxlength=80> <br>   



	<input type=hidden name = journal value ="H">
      <p>
      <INPUT TYPE="Radio" NAME="volume1" CHECKED onClick="no()">All years up to 2007 (volume 36)*
	  <INPUT TYPE="Radio" NAME="volume1" UNCHECKED onclick="yes()">From a specific year to present
      <div id="YDiv" style="visibility:hidden">
	<label for="Year">
	  <p>Enter year to search from: &nbsp;&nbsp;<INPUT TYPE="TEXT" VALUE="1969" NAME="volume" SIZE=4 MAXLENGTH=4><p>
	</label>
      </div> 
      <p>
      $pw_hidden
      <p><INPUT TYPE="SUBMIT" action="search.cgi">
      <INPUT TYPE="RESET" >
    </FORM>
<p>HTHP is now being published by OCP, Philadelphia, PA, USA (as of 2008, volume 37). Click on the link below to be taken to the new homepage:
<a href="http://www.oldcitypublishing.com/HTHP/HTHP.html">http://www.oldcitypublishing.com/HTHP/HTHP.html</a>.
<p>Online access to volumes prior to 2008 will remain exclusively available on this website.</p>
<p><p><font size=2><b>Advanced use</b> A space between keywords has the effect of an 'and' operator, and will produce results containing all the supplied keywords. The operator 'OR' between two keywords will match one or both keywords. Parentheses may be used for more complex searches. Search will attempt to match all standard variants of a word (plurals, gerunds etc). Double quotation marks around an expression will perform an exact search for that expression. All searches are case insensitive. Examples: 
      <br><b>thermophysical properties</b> will match documents containing both 'thermophysical' and 'properties'. <br><b>thermophysical or properties</b> will match documents containing either 'thermophysical' or 'properties' (or variants such as 'property'). <br><b>(thermophysical or thermochemical) properties</b> will match documents containing either 'thermophysical' and 'properties', or 'thermochemical' and 'properties'.
      <br> <b>"thermophysical properties"</b> (ie within double quotes) will match only the string 'thermophysical properties'.</font>
      <p>
END
print      $gtemplate->output;
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

  } else {
    print <<END;
      <div id="header">
      <a href="index.html">$banner</a>
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
	  </ul>
	</div>
      </div>
      <div id="title">
	<font size=4>
	<div class="left">$heading</div>
	<div class="center"></div>
	<div class="right"></div>
	</font>
      </div>
       <p>EPA abstracts are available from 1969, EPB from 1974, and EPC and EPD from 1983.<p><br>
      <form name="mainform" action="search.cgi" onsubmit="return validate();" method=get >
	
	Select journal to search:
	<input type=radio name = journal checked value = "X">&nbsp;All&nbsp;&nbsp;&nbsp;
	<input type=radio name = journal value = "A">&nbsp;EPA&nbsp;&nbsp;&nbsp;
	<input type=radio name = journal value = "B">&nbsp;EPB&nbsp;&nbsp;&nbsp;
	<input type=radio name = journal value = "C">&nbsp;EPC&nbsp;&nbsp;&nbsp;
	<input type=radio name = journal value = "D">&nbsp;EPD&nbsp;&nbsp;&nbsp;<p>
        
        Words or phrase:<br>
      &nbsp;&nbsp;<input type=text name = query size=32 maxlength=80> <br>
      Author (surname or initial followed by surname):<br>
      &nbsp;&nbsp;<input type=text name = authorquery size=32 maxlength=80> <br>   
	  
	  
	  <INPUT TYPE="Radio" NAME="volume1" CHECKED onClick="no()">Search all years
	  <INPUT TYPE="Radio" NAME="volume1" UNCHECKED onclick="yes()">Search from a specific year to present
      <div id="YDiv" style="visibility:hidden">
	<label for="Year">
	  <p>Enter year to search from: &nbsp;&nbsp;<INPUT TYPE="TEXT" VALUE="1969" NAME="volume" SIZE=4 MAXLENGTH=4><p>
	</label>
      </div>
      
      <p><INPUT TYPE="SUBMIT" action="search.cgi">
      <INPUT TYPE="RESET" >
    </FORM>
<p><p><font size=2><b>Advanced use</b> A space between keywords has the effect of an 'and' operator, and will produce results containing all the supplied keywords. The operator 'OR' between two keywords will match one or both keywords. Parentheses may be used for more complex searches. Search will attempt to match all standard variants of a word (plurals, gerunds etc). Double quotation marks around an expression will perform an exact search for that expression. All searches are case insensitive. Examples: 
      <br><b>urban planning</b> will match documents containing both 'urban' and 'planning' (as well as 'plan', 'plans', etc). <br><b>urban or planning</b> will match documents containing either 'urban' or 'planning'. <br><b>(urban or town) planning</b> will match documents containing either 'urban' and 'planning', or 'town' and 'planning'.
      <br> <b>"urban planning"</b> (ie within double quotes) will match only the string 'urban planning'.</font>
      <p>
END
print      $gtemplate->output;
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
  }
  
  print end_html; 
  exit;
}

if ($journal =~ /(A|B|C|D|X)/){
  $heading="<i>E&amp;P</i> search results: $query";
  $banner='<img src="Images/ep_left_ban.gif" alt="environment and planning" border=0 class="logo">' ;
  $buttons= <<END;
      <li><a href="A.html" title="Go to Environment and Planning A homepage">EPA&nbsp;homepage</a></li>
	  <li><a href="B.html" title="Go to Environment and Planning B homepage">EPB&nbsp;homepage</a></li>
	  <li><a href="C.html" title="Go to Environment and Planning C homepage">EPC&nbsp;homepage</a></li>
	  <li><a href="D.html" title="Go to Environment and Planning D homepage">EPD&nbsp;homepage</a></li>
	  <li><a href="index.html" title="Go to Environment and Planning homepage">EP&nbsp;homepage</a></li>
END
}
elsif ($journal =~/(P|V)/){
  $heading="<i>Perception</i> search results: $query $authorquery";
  $banner='<img src="Images/p_ban2.gif" alt="Perception" border=0 class="logo">';
  $buttons="<li><a href=\"P.html\" title=\"Go to Perception homepage\">Perception&nbsp;homepage</a></li>"
} elsif ($journal =~ /H/) {
  $heading="<i>High Temperatures &#8211; High Pressures</i> search results: $query $authorquery";
  $banner='<img src="Images/h_ban2.gif" alt="High Temperatures &#8211; High Pressures" border=0 class="logo">';
  $buttons="<li><a href=\"H.html\" title=\"Go to HTHP homepage\">HTHP&nbsp;homepage</a></li>"
}
else {$heading = "Pion journal search results"; 
     }

print <<END;
    <div id="header">
    <a href="index.html">$banner</a>
    <a href="http://www.pion.co.uk"><img src="Images/right_ban.gif" alt="Pion Ltd" class="pionlogo" /></a>
  </div>
  <div id="total">
    <div id="top-buttons">
      <div class="topnavigation">
        <ul>
          $buttons
	  <li><a href="http://www.pion.co.uk" title="Go to Pion ltd homepage">Pion&nbsp;homepage</a></li>
	  </ul>
        </ul>
      </div>
    </div>
    <div id="title">
      <font size=4>
      <div class="left">$heading</div>
      <div class="center"></div>
      <div class="right"></div>
      </font>
    </div>
END



$query =~ s/\s*$//g;  # remove trailing spaces
$authorquery =~ s/\s*$//g;
# assume that $authorquery is given


if($authorquery){ 
  #modify to allow "firstname lastname" searches
  #print p, "Search authors for '$query'";
  
  # if xxxx yyyy assume firstname lastname
  $authorquery=~s/^\s+//g;
  $authorquery_quoted=$dbh->quote($authorquery); 

  if($authorquery=~/(\w)\w*\s+(\w+)/){
    #print "$1...$2...";
    $fname_quoted="'$1%'";
    $lname_quoted=$dbh->quote($2.'%');
    $lname_norm_quoted=$dbh->quote(unidecode(decode_entities($2)).'%');
    
    $auquery_quoted="(last_name ilike $lname_quoted or last_name_normalised ilike $lname_norm_quoted or last_name_normalised ilike '$authorquery') and (first_name ilike $fname_quoted or last_name_normalised ilike $authorquery_quoted)";
    #$auquery_quoted="last_name ilike $lname_quoted and first_name ilike $fname_quoted";
     #print "xxxxx $query_quoted";
     #print "xx$authorquery xx";
  } else { 
    
    $lname_norm_quoted=$dbh->quote(unidecode(decode_entities($authorquery)).'%');
    $auquery_quoted= "(last_name ilike ".$dbh->quote($authorquery.'%')." or last_name_normalised ilike $lname_norm_quoted or last_name_normalised ilike $authorquery_quoted)";
  } 
  
  $auquerystring="and papers.paperid in (select authors.paperid from authors where $auquery_quoted)"; 
  $querystring1="select title, journal, year, volume, issue, start_page, end_page, papers.paperid, '', position from authors, papers where authors.paperid=papers.paperid and $auquery_quoted and $searchstring order by year DESC, position LIMIT $limit OFFSET $offset";
#print $querystring;
}


if($query)
{
  #print p, "Search abstracts for '$query'";
  #if ($exact eq 'on' or $query=~/^\s*".*"\s*$/){print br, "Match this exact string only.";}
  if($exact eq 'on' or $query=~/^\s*".*"\s*$/){
    print br, "Matching exact string only.";
    $query_quoted= $dbh->quote($query);
    $query_quoted =~ s/\s+/\&/g;
    $query_quoted =~ s/\s+or\s+/|/gi;
    $query_quoted =~ s/"//g;  
    $query =~ s/^\s*"(.*)"\s*$/$1/;
    $query =~ s/\s+/\\s+/g;
    $query2_quoted = $dbh->quote($query);
  
    # Exact string
    $querystring="select title, journal, year, volume, issue, start_page, end_page, paperid, headline(docs(papers), to_tsquery($query_quoted)), rank(doc(papers),to_tsquery($query_quoted)) as rel from papers where doc(papers) @@ to_tsquery($query_quoted) and $searchstring and (title ~* $query2_quoted or abstract ~* $query2_quoted) $auquerystring order by year DESC LIMIT $limit OFFSET $offset";} 
  else {
    $qy_quoted=  $dbh->quote($query);
    $qy_quoted =~ s/\s+/\&/g;
    $qy_quoted =~ s/\s+or\s+/|/gi;
    $qy_quoted =~ s/"//g;
    $qy2=$query;  
    $qy2 =~ s/^\s*"(.*)"\s*$/$1/;
    $qy2 =~ s/\s+/\\s+/g;
    $qy2_quoted = $dbh->quote($qy2);  
    
    $query =~ s/\s+/\&/g;
    $query =~ s/\s+or\s+/|/gi;
    $query_quoted= $dbh->quote($query);
    #search titles and abstacts
    $querystring="select DISTINCT title, journal, year, volume, issue, start_page, end_page, paperid, headline(docs(papers), to_tsquery($query_quoted)), rank(doc(papers),to_tsquery($query_quoted)) as rel from papers where doc(papers) @@ to_tsquery($query_quoted) and $searchstring $auquerystring order by rel DESC, year DESC LIMIT $limit OFFSET $offset 
       ";
    #union
    
    #select title, journal, year, volume, issue, start_page, end_page, paperid, headline(docs(papers), to_tsquery($query_quoted)), 1000 as rel from papers where doc(papers) @@ to_tsquery($query_quoted) and $searchstring and (title ~* $qy2_quoted or abstract ~* $qy2_quoted)
    
 
  }
}


#$querystring="select title, journal, year, volume, issue, start_page, end_page, paperid, headline(abstract, q), rank(vectors, q) from papers, to_tsquery($query_quoted) as q where vectors @@ q and $searchstring order by rank(vectors, q) DESC, year DESC";

#$querystring="select title, journal, year, volume, issue, start_page, end_page, paperid, headline(abstract, to_tsquery($query_quoted)), rank(to_tsvector(abstract),to_tsquery($query_quoted)) as rel from papers where to_tsvector(abstract) @@ to_tsquery($query_quoted) and $searchstring order by rel DESC, year DESC";

#$querystring="select title, journal, year, volume, issue, start_page, end_page, paperid, headline(title||abstract, to_tsquery($query_quoted)), rank(to_tsvector(title||abstract),to_tsquery($query_quoted)) as rel from papers where to_tsvector(title||abstract) @@ to_tsquery($query_quoted) and $searchstring order by rel DESC, year DESC";


#search titles and abstacts
#$querystring="select title, journal, year, volume, issue, start_page, end_page, paperid, headline(docs(papers), to_tsquery($query_quoted)), rank(doc(papers),to_tsquery($query_quoted)) as rel from papers where doc(papers) @@ to_tsquery($query_quoted) and $searchstring order by rel DESC, year DESC";


# Exact string
#$querystring="select title, journal, year, volume, issue, start_page, end_page, paperid, headline(docs(papers), to_tsquery($query_quoted)), rank(doc(papers),to_tsquery($query_quoted)) as rel from papers where doc(papers) @@ to_tsquery($query_quoted) and $searchstring and (title ~* $query_quoted or abstract ~* $query_quoted) order by rel DESC, year DESC";

#$querystring=$querystring1 unless $query; # assume author-only search unless text query given

unless ($query){
  $type='A'; $querystring=$querystring1 }
else {
  $type='S'}

#print p,"q= $querystring";

print p, b('Search results continued...') if $results_page>0;

$sth=$dbh->prepare($querystring) || die;
$sth->execute()||die "Can't execute query\n";

$count=0;
while (@result=$sth->fetchrow()){
  #print "$rank, $year";
  $count++;
  ($title, $jrnl, $pyear, $volume, $pissue, $start_page, $end_page, $paperid, $headline, $rank)=@result;

  $paperid =~ s/\s*$//; # delete trailing spaces
  $pw_string="\&pw=1" if $pw==1;
  
  $pagerange="$start_page<font size='-1'>&nbsp;</font>&#8211;<font size='-1'>&nbsp;</font>$end_page" if $start_page;
  print '<font size="-2"><br></font>';
  if ($start_page == 0 && $jrnl ne 'V'){
    print "<p><font size=-1><i>$jname{$jrnl}</i> $pyear advance online publication </font><br><a href=\"abstract.cgi?id=$paperid$pw_string\"><b>$title</b></a><br>\n";
  } 
  elsif ($jrnl eq 'V') {
      print "<p><font size='-1'><i>Perception</i> <b>$volume</b> <i>ECVP Abstract Supplement</i> $pyear</font><br><a href=\"abstract.cgi?id=$paperid\"><b>$title</b></a><br>\n";
    } elsif ($jrnl eq 'H' && $volume==27) {
      print "<p><font size=-1><i>$jname{$jrnl}</i> 1995/1996 <b>27/28</b> $pagerange </font><br><a href=\"abstract.cgi?id=$paperid$pw_string\"><b>$title</b></a><br>\n";
    } elsif ($jrnl eq 'H' && $volume==35) {
      print "<p><font size=-1><i>$jname{$jrnl}</i> 2003/2007 <b>35/36</b> $pagerange </font><br><a href=\"abstract.cgi?id=$paperid$pw_string\"><b>$title</b></a><br>\n";
    }
  else {
     print "<p><font size=-1><i>$jname{$jrnl}</i> $pyear <b>$volume</b> $pagerange </font><br><a href=\"abstract.cgi?id=$paperid$pw_string\"><b>$title</b></a><br>\n";
   }
  
  
  $authquery=$dbh->prepare("select first_name, last_name, suffix from authors where paperid='$paperid' order by position")||die;
  $authquery->execute()||die;
  $authors="";
  while (@author=$authquery->fetchrow()){
    ($first_name,$last_name,$suffix)=@author;
    $suffix='&nbsp;'.$suffix if $suffix;
    $authors .= "$first_name $last_name$suffix, ";
  }
  $authors =~ s/, $//;   # remove final comma space
  $authors =~ s/($authorquery)/<b>$1<\/b>/gi if $authorquery;
  if ($type eq 'A'){
    
    print "$authors<br>\n"
  } 
  else {
    print "$authors<br><font size=-1>\"...$headline...\"</font><br>\n";
  }
  #print '<br>';
}


$pw_sting='&amp;pw=1';
#$prev_page=$results_page-1;
#print "<p><a href='search.cgi?journal=$journal&amp;year=$year&amp;type=$type&amp;issue=$issue$pw_string&amp;query=$query_orig&respage=$prev_page'>Previous results</a>" if $results_page>0;
if ($count==$limit){
  $next_page=$results_page+1;

  print "<p><a href='search.cgi?journal=$journal&amp;year=$year&amp;type=$type&amp;issue=$issue&amp;authorquery=$authorquery&amp;query=$query_orig&respage=$next_page'>More results</a>"}
else{print "<p>No matching results found. <p><a href='search.cgi?journal=$journal'>Refine search</a>" if ($count==0 && $results_page==0)}


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
