/* r04: exact Delta of G_c = F_c o J o F_c on GR(4,m) in Teichmuller digits, via the digit formulas
 *   (a,b)+(u,v) = (a+u, b+v+sqrt(au)),   (y0,y1)-(z0,z1) = (y0+z0, y1+z0+z1+sqrt(y0 z0)).
 * Field F_q = GF(2)[x]/(f_m) with the fixed polynomials below (bit i = coefficient of x^i).
 * c = the cidx-th element (increasing integer order) with Tr(c)=1. Element (a,b) <-> index a*q+b.
 * Usage: gc_ddt_v2 m cidx K k  -> directions alpha in {1..N-1} with alpha = k (mod K).
 * Output (one line, only on success, exit 0):
 *   SHARD m= poly= cidx= c= K= k= ndirs= alphasum= best= alpha= beta= perm=1
 * Exit codes: 2 bad arguments, 3 internal check failed (trace, D(a)=0, not a permutation).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
static int m, q; static unsigned poly;
static unsigned short *mul_tab, *sq_root;
static unsigned gmul_slow(unsigned a, unsigned b){ unsigned r=0; while(b){ if(b&1) r^=a; b>>=1; a<<=1; if(a&q) a^=poly; } return r; }
static int parse_int(const char*s, long lo, long hi, long*out){ char*e; errno=0; long v=strtol(s,&e,10);
  if(errno||*s=='\0'||*e!='\0'||v<lo||v>hi) return 0;
  *out=v; return 1; }
int main(int argc, char**argv){
  long lm,lc,lK,lk;
  if(argc!=5){fprintf(stderr,"usage: gc_ddt_v2 m cidx K k\n");return 2;}
  if(!parse_int(argv[1],1,10,&lm)){fprintf(stderr,"bad m (1..10)\n");return 2;}
  if(!parse_int(argv[2],0,1L<<20,&lc)){fprintf(stderr,"bad cidx\n");return 2;}
  if(!parse_int(argv[3],1,4096,&lK)){fprintf(stderr,"bad K (>=1)\n");return 2;}
  if(!parse_int(argv[4],0,lK-1,&lk)){fprintf(stderr,"bad k (0<=k<K)\n");return 2;}
  m=(int)lm; int cidx=(int)lc, K=(int)lK, k0=(int)lk;
  static const unsigned polys[]={0,0x3,0x7,0xB,0x13,0x25,0x43,0x83,0x11B,0x211,0x409};
  q=1<<m; poly=polys[m];
  mul_tab=malloc(sizeof(unsigned short)*(size_t)q*q); sq_root=malloc(sizeof(unsigned short)*q);
  if(!mul_tab||!sq_root){fprintf(stderr,"oom\n");return 3;}
  for(int a=0;a<q;a++) for(int b=0;b<q;b++) mul_tab[a*q+b]=gmul_slow(a,b);
  #define MUL(a,b) mul_tab[(a)*q+(b)]
  for(int a=0;a<q;a++) sq_root[MUL(a,a)]=a;
  int c=-1,cnt=0;
  for(int a=0;a<q;a++){ unsigned t=a,s=a; for(int i=1;i<m;i++){ t=MUL(t,t); s^=t; }
    if(s>1){fprintf(stderr,"trace err\n");return 3;} if(s==1){ if(cnt==cidx){c=a;break;} cnt++; } }
  if(c<0){fprintf(stderr,"no c with this cidx\n");return 2;}
  int N=q*q;
  unsigned short *G0=malloc(sizeof(unsigned short)*N), *G1=malloc(sizeof(unsigned short)*N);
  unsigned char *seen=calloc(N,1); int *count=malloc(sizeof(int)*N);
  if(!G0||!G1||!seen||!count){fprintf(stderr,"oom\n");return 3;}
  for(int a=0;a<q;a++) for(int b=0;b<q;b++){
    unsigned Da=MUL(a,a)^a^c; if(Da==0){fprintf(stderr,"D(a)=0\n");return 3;}
    unsigned L=MUL(Da,b); unsigned DL=MUL(L,L)^L^c;
    G0[a*q+b]=L; G1[a*q+b]=MUL(DL,a); int y=G0[a*q+b]*q+G1[a*q+b];
    if(seen[y]){fprintf(stderr,"not a permutation\n");return 3;} seen[y]=1; }
  int best=0,bestal=-1,bestbe=-1; long ndirs=0; unsigned long long alsum=0;
  for(int al=k0; al<N; al+=K){ if(al==0) continue; ndirs++; alsum+=(unsigned long long)al;
    int u=al/q, v=al%q; memset(count,0,sizeof(int)*N);
    for(int a=0;a<q;a++){ unsigned a2=a^u; unsigned carry=sq_root[MUL(a,u)];
      for(int b=0;b<q;b++){ unsigned b2=b^v^carry; int x=a*q+b, y=a2*q+b2;
        unsigned y0=G0[y],y1=G1[y],z0=G0[x],z1=G1[x];
        unsigned d0=y0^z0, d1=y1^z0^z1^sq_root[MUL(y0,z0)];
        int j=d0*q+d1; if(++count[j]>best){best=count[j];bestal=al;bestbe=j;} } } }
  printf("SHARD m=%d poly=0x%X cidx=%d c=%d K=%d k=%d ndirs=%ld alphasum=%llu best=%d alpha=%d beta=%d perm=1\n",
         m,poly,cidx,c,K,k0,ndirs,alsum,best,bestal,bestbe);
  if(fflush(stdout)!=0) return 3;
  return 0;
}
