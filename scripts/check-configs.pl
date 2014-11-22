# By Paul Bolle October 2014.
#
# Contributed to the public domain by its author.

use 5.016;
use warnings;
use autodie;

use File::Find;

my @Kconfigs;

my $Kconfigre = qr/Kconfig.*/;
my $configre = qr/^\s*(menu)?config\s+(?<config>(\w+))$/;
my $CONFIG_re = qr/\bCONFIG_(?<CONFIG_>(\w+))/;

sub match {
	push( @Kconfigs, $File::Find::name ) if ($_ =~ $Kconfigre);
}

sub parse_kconfig {
	my ($path) = @_;

	my @ret;

	open( my $kconfig, "<", $path );
	my $slurp = do { local $/ = undef; <$kconfig> };
	close( $kconfig );
	my @lines = split ( /\n/, $slurp );
	foreach my $line (@lines) {
		if ($line =~ /$configre/) {
			push( @ret, $+{config} );
		}
	}

	@ret;
}

sub parse_shipped {
	my ($path) = @_;

	my @ret;

	open( my $shipped, "<", $path );
	my $slurp = do { local $/ = undef; <$shipped> };
	close( $shipped );
	my @lines = split ( /\n/, $slurp );
	my $i = 1;
	foreach my $line (@lines) {
		if ($line =~ /$CONFIG_re/) {
			push( @ret, [$i, $+{CONFIG_}] );
		}
		$i++;
	}

	@ret;
}

exit main ( @ARGV );

sub main {
	my %configs;

	find( \&match, @_ );

	foreach my $Kconfig (@Kconfigs) {
		my (@tmp) = parse_kconfig( $Kconfig );
		foreach my $config ( @tmp ) {
			$configs{ $config }++;
		}
	}

	foreach my $shipped (glob("config-*")) {
		my (@tmp) = parse_shipped( $shipped );
		foreach my $ref ( @tmp ) {
			say( STDERR "$shipped:$ref->[0]: No Kconfig symbol matches 'CONFIG_$ref->[1]'" )
				unless (grep( /$ref->[1]/, keys( %configs )));
		}
	}

	0;
}

