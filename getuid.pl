use CGI::Cookie;
use Digest::SHA1 qw(sha1_hex);
sub get_uid(){
  # this returns the uid from the cookie, or 0 if no valid cookie
  # optional parameter: $matchcode,  then function returns uid if client subscribes
  # this does not yet handle archive separately, just complete journals
  
  my $matchcode=$_[0]; 
  my $journal=$_[1];
  #my $year=$_[2]; 
  my %cookies = CGI::Cookie->fetch();
  
  if ($cookies{user} && $cookies{auth}) {
    $username=$cookies{user}->value; 
    my $sth=$dbh->prepare("select uid,token, client_refno, allowed_journals from passwd where username='$username'");
    
    #print p, "select uid,token from passwd where username='$username'";
    $sth->execute();
    my ($uid,$token,$cli,$allowed_journals)=$sth->fetchrow();
    
    my $auth_string = sha1_hex($cookies{user}->value . ":" . $token);
    #  print p, $cookies{user}, p, $cookies{auth}, p, $auth_string;
    #}
    
    #print p, $auth_string,p,$cookies{auth}->value;
    
    if ($auth_string eq $cookies{auth}->value){
      if ($cli && $matchcode){
       $sth=$dbh->prepare("select count(*) from subscribers where client=$cli and prod  ~ '$matchcode'");
       $sth->execute();
       my($prodcount)=$sth->fetchrow;
       #print "Debug: $prodcount";
       if ($prodcount) {return $uid}
       else {return 0}
      }
      elsif($allowed_journals){
        #print "aaaa $allowed_journals";
        if($allowed_journals=~/$journal/){return $uid}
        else {return 0}
      }
      else {return $uid};
    }
    else {
      return 0;
    }
  } 
  else {
    return 0;
  }
}
1;