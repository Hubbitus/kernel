# Hubbitus kernel


My primary goal long time to build kernel for home desktop use. It should be preemptive. Speed and memory efficiency much more interesting what high stability.

With that aim but being [Fedora maintainer](https://fedoraproject.org/wiki/PavelAlexeev) I want also use Fedora distribution kernel with their patches, support (although partial) and love.

## The most famous and interesting for me futures

* [ZRAM](https://en.wikipedia.org/wiki/Zram) - In-memory compressed swap disks. Successor of [ZCACHE](http://lwn.net/Articles/562254/) which I had prefer before - unfortunately was dropped development.
	Although that module already enabled in Fedora kernel, but:
 - I prefer use it with high performance [lz4](https://code.google.com/p/lz4/) compression algorithm which promise much more performance especially on read, even than `lzo`.
 - I also use [being on review packaged ZRAM systemd service zram](https://bugzilla.redhat.com/show_bug.cgi?id=1169926), which allow enable use it just like:
```
	systemctl enable zram
	systemctl start zram
```
For details and user space utilities please look at aforementioned package.
* [UKSM](http://kerneldedup.org/en/) - Ultra Kernel Samepage Merging. Idea is great and simple - yuo do not want spent memory twice for one data, is not? Think it as runtime deduplication.
 - You hen may with try [uksmtools](http://hubbitus.info/rpm/Fedora20/uksmtools/)
* [BFQ](http://algo.ing.unimo.it/people/paolo/disk_sched/) - Budget Fair Queueing (BFQ) Storage-I/O Scheduler
* [BFS](https://en.wikipedia.org/wiki/Brain_Fuck_Scheduler) - Brain Fuck Scheduler
	*If you are working not on mainframe and scaling to 4096 process core is not required for you. But budget HDD is botlneck for awaiting start even simple application by 2-10 seconds - you should like that pair*.
* AND some additions like [TuxOnIce (TOI)](http://tuxonice.nigelcunningham.com.au/), GCC patch, bug fixes when you choose [PF (Post-factum)](https://pf.natalenko.name/) kernel build.

### What is here

I'll try follow Fedora stable kernel releases in main stable release of distribution. Now it is Fedora 21.

Binary builds (and src.rpm also) you could find in my repository: http://hubbitus.info/rpm/.
[Instructions](http://hubbitus.info/wiki/Main) to enable it for automatically install and update packages.

Now it represent [Pf3 3.17 build](https://pf.natalenko.name/forum/index.php?topic=279.0).

Questions, suggestions, bugreports always welcome!

## License

As that repository forked from [Fedora kernel](http://pkgs.fedoraproject.org/cgit/kernel.git/) respect it [licensed under MIT](https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing#License_of_Fedora_SPEC_Files).