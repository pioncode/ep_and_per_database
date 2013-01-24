#!/bin/perl
# getpdf.cgi?id=....&vol=...

# redirects browser to an IP-restricted PDF if valid cookie


use DBI;
use CGI qw(:standard -no_xhtml);
require('getuid.pl');

@weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
$thisyear = 1900 + $yearOffset;
$month++;

$id=secure(param('id'));
#$vol=secure(param('vol'));

%pdfpath= (
 "P" => "perception/fulltext/p",
 "A" => "epa/fulltext/a",
 "B" => "epb/fulltext/b",
 "C" => "epc/fulltext/c",
 "D" => "epd/fulltext/d",
 "H" => "hthp/fulltext/h"
);

#$id=~/^(.).*/;
#$journal=uc($1);
$dbh = DBI->connect("dbi:Pg:dbname=journals;host=localhost;port=5432", "jon", "") || die "couldn't connect";
$sth=$dbh->prepare("select year, journal, title, volume, issue, page_prefix, start_page, end_page from papers where paperid='$id';") || die;
$sth->execute()|| die "Can't execute query\n";
#print  'xx';#
@result=$sth->fetchrow();
($year, $journal, $title, $volume, $issue, $page_prefix, $start_page, $end_page)=@result;

if ($start_page){
   $matchcode= "$journal.*".substr($year, 2, 2)} # a normal paginated article
else {
   $matchcode= "$journal.*".substr($thisyear, 2, 2) # a forthcoming article - check for current subscription
}
#test if valid password (ie session cookie)
$volume_padded=sprintf("%02d", $volume);
$uid=get_uid($matchcode,$journal);
print header;

if ($uid){
  if($id){
    $thisip=$ENV{REMOTE_ADDR};
    mkdir("fulltext_temp/$uid") unless -e "fulltext_temp/$uid";
    open (HTACCESS, ">fulltext_temp/$uid/.htaccess");
    print HTACCESS <<EOF;
AuthUserFile /dev/null
AuthGroupFile /dev/null
AuthName ARestrict
AuthType Basic
ErrorDocument 403 /ep/access_error.html
<Limit GET>
order allow,deny
allow from $thisip
</Limit>
EOF
    close HTACCESS;
    #$id=~/^(.).*/;
    #$journal=uc($1);
    if ($start_page==0){$subdir='forth'} else {$subdir=$volume_padded}
    $pdforig='../../'.$pdfpath{$journal}.$subdir."/$id.pdf";
    #print start_html(-title=>'Downloading PDF...', -head=>meta({-http_equiv => 'Refresh', -content=>'application/pdf', -url=>"=fulltext_temp/$uid/$id.pdf"}));
    #print start_html(-title=>'Downloading PDF...');
    #print "$pdforig fulltext_temp/$uid/$id.pdf";
    unless (-e "fulltext_temp/$uid/$id.pdf"){
      symlink($pdforig, "fulltext_temp/$uid/$id.pdf");
    }
    print start_html(-title=>'Downloading PDF...', -onLoad=>"location.href='fulltext_temp/$uid/$id.pdf'");
    print p, h1('Full-text download'),p, "If PDF doesn't download automatically, please <a href='fulltext_temp/$uid/$id.pdf'>click here</a>";
    print end_html; 
    system("echo \"rm /htdocs/fulltext_temp/$uid/$id.pdf\"|at now + 1 hours");
      #### assumes symlink
  } else {print start_html{-title=>'Downloading PDF...'}, "not enough info";exit}
}
else{
# access denied!
    print p, start_html{-title=>'Downloading PDF...'}, "Sorry, access denied", end_html;
    
}

sub secure{
  #return only a single block of alphanumerics to prevent SQL hacking, etc 
  my $input=$_[0];
  $input=~s/\W//g; # delete any non-alpha chars
  return $input;
}
