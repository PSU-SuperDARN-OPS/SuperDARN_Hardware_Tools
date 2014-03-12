#include <errno.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <math.h>
#include <netdb.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <sys/stat.h>
#ifdef __QNX__
  #include <hw/pci.h>
  #include <hw/inout.h>
  #include <sys/neutrino.h>
  #include <sys/mman.h>
#endif

#define SWITCHES 0
#define ATTEN    1
#define READ     0
#define WRITE    1
#define ON       1
#define OFF      0

#define NEW_PMAT 1 

#define CARDS 200 
#define ANTS 16 
#define FREQS 1500
#define TRIM_LENGTH_METERS 117.317 
#define VELOCITY_FACTOR 0.87

int stupid_flag=0;
int test_flag=-1000;
int sock=-1;
int verbose=2;
char *hostip="192.168.0.11";
char *file_prefix="kodiak_superdarn";
char *file_ext=".txt";
char filename[120];
char *dir="./kodiak_long_cables/";
FILE *fp=NULL;
int port=23;
char command[80];
char input[80];
char freq_start[10]="300E3";
char freq_stop[10]="20E6";
char freq_steps[10]="201";

struct timeval t0,t1,t2,t3,t4,t5,t6;
struct timeval t10,t11;
unsigned long elapsed;

int opentcpsock(char *hostip, int port);

int mlog_data_command(char *command,double *array[FREQS],int b) {
  int count,rval,sample_count;
  char output[10]="";
  char command2[80];
  char cmd_str[80],prompt_str[10],data_str[1000];
  int cr,lf;
  struct timeval tick,tock;
      strcpy(command2,command);
      if (verbose>2) printf("%d Command: %s\n",strlen(command2),command2);
      write(sock, &command2, sizeof(char)*strlen(command2));
      cr=0;
      lf=0;
      count=0;
      if (verbose>2) fprintf(stdout,"Command Output String::\n");
      strcpy(cmd_str,"");
      gettimeofday(&tick,NULL);
      while((cr==0) || (lf==0)){
        gettimeofday(&tock,NULL);
        if(tock.tv_sec-tick.tv_sec>1) {
         printf("TIMEOUT: Data Command : %s\n",command2);
         return -1;
        }
        rval=read(sock, &output, sizeof(char)*1);
        if (rval<1) {
#ifdef __QNX__
          delay(1);
#else
          usleep(10);
#endif
        } else {
          gettimeofday(&tick,NULL);
        }
        if (output[0]==13) {
          cr++;
          continue;
        }
        if (output[0]==10) {
          lf++;
          continue;
        }
        count+=rval;
        strncat(cmd_str,output,rval);
        if (verbose>2) fprintf(stdout,"%c",output[0]);
      }
      if (verbose>2) printf("Processing Data\n");

      cr=0;
      lf=0;
      count=0;
      sample_count=0;
      if (verbose>2) fprintf(stdout,"\nData Output String::\n");
      strcpy(data_str,"");
      if (verbose>2) fprintf(stdout,"%d: ",sample_count);
      gettimeofday(&tick,NULL);
      while((cr==0) || (lf==0)){
        gettimeofday(&tock,NULL);
        if(tock.tv_sec-tick.tv_sec>1) {
         printf("TIMEOUT: Data Command : %s\n",command2);
         return -1;
        }
        rval=read(sock, &output, sizeof(char)*1);
        if (rval<1) {
#ifdef __QNX__
          delay(1);
#else
          usleep(10);
#endif
        } else {
          gettimeofday(&tick,NULL);

          if (output[0]==13) {
            cr++;
            continue;
          }
          if (output[0]==10) {
            lf++;
            continue;
          }
          if(output[0]==',') {
             if((sample_count % 2) == 0) {
               if (sample_count/2 >=FREQS) {
                 printf("ERROR: too many samples... aborting\n");
                 exit(-1);
               }
               array[sample_count/2][b]=atof(data_str);
               if (verbose>2) fprintf(stdout,"%s  ::  %lf",data_str,array[sample_count/2][b]);
             }
             sample_count++;
             if (verbose>2) fprintf(stdout,"\n%d: ",sample_count);
             strcpy(data_str,"");
          } else {
             strncat(data_str,output,rval);
          }
        }
      }
      if((sample_count % 2) == 0) {
        if (sample_count/2 >=FREQS) {
          printf("ERROR: too many samples... aborting\n");
          exit(-1);
        }
        array[sample_count/2][b]=atof(data_str);
        if (verbose>2) fprintf(stdout,"%s  ::  %lf",data_str,array[sample_count/2][b]);
      }
      sample_count++;
      strcpy(data_str,"");
      if (verbose>2) fprintf(stdout,"\nSamples: %d\n",sample_count/2);
      if (verbose>2) fprintf(stdout,"\nPrompt String::\n");
      while(output[0]!='>'){
        rval=read(sock, &output, sizeof(char)*1);
#ifdef __QNX__
        if (rval<1) delay(1);
#else
        if (rval<1) usleep(10);
#endif
        strncat(prompt_str,output,rval);
        if (verbose>2) fprintf(stdout,"%c",output[0]);
      }
  return 0;
}

int button_command(char *command) {
  int count,rval;
  char output[10]="";
  char command2[80];
  char prompt_str[80];
  struct timeval tick,tock;
/*
*  Process Command String with No feedback 
*/
      strcpy(command2,command);
      if (verbose>2) fprintf(stdout,"%d Command: %s\n",strlen(command2),command2);
      write(sock, &command2, sizeof(char)*strlen(command2));
      count=0;
      if (verbose>2) fprintf(stdout,"\nPrompt String::\n");
      gettimeofday(&tick,NULL);
      while(output[0]!='>'){
        gettimeofday(&tock,NULL);
        if(tock.tv_sec-tick.tv_sec>1) {
         printf("TIMEOUT: Button Command : %s\n",command2);
         return -1;
        }
        rval=read(sock, &output, sizeof(char)*1);
        strncat(prompt_str,output,rval);
        if(rval>0) gettimeofday(&tick,NULL);
        if (verbose>2) fprintf(stdout,"%c",output[0]);
        count++;
      }
      if (verbose>2) fprintf(stdout,"Command is done\n",command2);
      fflush(stdout);

  return 0;

}
void mypause ( void ) 
{ 
  fflush ( stdin );
  printf ( "Press [Enter] to continue . . ." );
  fflush ( stdout );
  getchar();
} 

int main(int argc, char **argv)
{
  char output[40],strout[40];
  char cmd_str[80],prompt_str[10],data_str[1000];
  double *phase[FREQS],*pwr_mag[FREQS];
  double freq[FREQS];
  int rval,count,sample_count,fail,cr,lf;
  int i=0,new_ant=0,ant=0,iter=0,data=0,index=0; 
  double fstart;
  double fstop;
  double fstep;
  int fnum;
  int radar;
  unsigned int portA0,portB0,portC0,cntrl0 ;
  unsigned int portA1,portB1,portC1,cntrl1 ;
	int		 temp, pci_handle, j,  IRQ  ;
	unsigned char	 *BASE0, *BASE1;
	unsigned int	 mmap_io_ptr,IOBASE, CLOCK_RES;
	float		 time;


	float	pwr_min, pwr_max, pwr_avg, pwr;
	float	phi_min, phi_max, phi_avg, phi;
	float	length_min, length_max, length_avg, length;
	float	lambda;


#ifdef __QNX__
	struct		 _clockperiod new, old;
	struct		 timespec start_p, stop_p, start, stop, nsleep;
#endif
/*
    if(argc <3 ) {
      fprintf(stderr,"%s: invoke with ant number and iteration number\n",argv[0]);
      fflush(stderr);
      exit(0);
    }
    if(argc >=3 ) {
      ant=atoi(argv[1]);
      iter=atoi(argv[2]);
    }
*/
/*
    if(argc ==4 ) {
      test_flag=atoi(argv[3]);
      ant=atoi(argv[2]); 
    } else {
      test_flag=-1000;
    } 
    radar=atoi(argv[1]);
    printf("Radar: %d\n",radar);
    printf("Test flag: %d\n",test_flag);
    switch(radar) {
      case 1:
        break;
      case 2:
        break;
      case 3:
        break;
      default:
        fprintf(stderr,"Invalid radar number %d",radar);
        exit(-1);
    } 
*/
    /* SET THE SYSTEM CLOCK RESOLUTION AND GET THE START TIME OF THIS PROCESS */
        fflush(stderr);
#ifdef __QNX__
	new.nsec=10000;
	new.fract=0;
	temp=ClockPeriod(CLOCK_REALTIME,&new,0,0);
	if(temp==-1){
		perror("Unable to change system clock resolution");
	}
	temp=clock_gettime(CLOCK_REALTIME, &start_p);
	if(temp==-1){
		perror("Unable to read sytem time");
	}
	temp=ClockPeriod(CLOCK_REALTIME,0,&old,0);
	CLOCK_RES=old.nsec;
	printf("CLOCK_RES: %d\n", CLOCK_RES);
#endif
  fnum=atoi(freq_steps);
  fstart=atof(freq_start);
  fstop=atof(freq_stop);
  fstep=(fstop-fstart)/(fnum-1);

  for(i=0;i<fnum;i++) {
    freq[i]=fstart+i*fstep;
    phase[i]=calloc(1,sizeof(double));
    pwr_mag[i]=calloc(1,sizeof(double));
  }

  printf("\nPreparing for Antenna Measurements\n");


  // Open Socket and initial IO
    if (verbose>0) printf("Opening Socket %s %d\n",hostip,port);
    sock=opentcpsock(hostip, port);
    if (sock < 0) {
      if (verbose>0) printf("Socket failure %d\n",sock);
    } else if (verbose>0) printf("Socket %d\n",sock);
    rval=read(sock, &output, sizeof(char)*10);
    if (verbose>0) fprintf(stdout,"Initial Output Length: %d\n",rval);
    strcpy(strout,"");
    strncat(strout,output,rval);
    if (verbose>0) fprintf(stdout,"Initial Output String: %s\n",strout);
// *****************************************************************************
    sprintf(command,":SENS1:FREQ:STAR %s\r\n",freq_start);
    button_command(command);
    sprintf(command,":SENS1:FREQ:STOP %s\r\n",freq_stop);
    button_command(command);
    sprintf(command,":SENS1:SWE:POIN %s\r\n",freq_steps);
    button_command(command);
    button_command(":CALC1:PAR:COUN 2\r\n");
    button_command(":CALC1:PAR1:SEL\r\n");
    button_command(":CALC1:PAR1:DEF S22\r\n");
    button_command(":CALC1:FORM UPH\r\n");
    button_command(":CALC1:PAR2:SEL\r\n");
    button_command(":CALC1:PAR2:DEF S22\r\n");
    button_command(":CALC1:FORM MLOG\r\n");
    button_command(":SENS1:AVER OFF\r\n");
    button_command(":SENS1:AVER:COUN 4\r\n");
    button_command(":SENS1:AVER:CLE\r\n");
    button_command(":INIT1:CONT ON\r\n");
// *******************************************************************************

/* Old net analy setup routine
    button_command(":SYST:PRES\r\n");



    printf("\n\n\7\7Calibrate Network Analyzer for S12,S21\n");
    mypause();
    button_command(":SENS1:CORR:COLL:METH:THRU 1,2\r\n");
    sleep(1);
    button_command(":SENS1:CORR:COLL:THRU 1,2\r\n");
    printf("  Doing S1,2 Calibration..wait 4 seconds\n");
    sleep(4);

    button_command(":SENS1:CORR:COLL:METH:THRU 2,1\r\n");
    sleep(1);
    button_command(":SENS1:CORR:COLL:THRU 2,1\r\n");
    printf("  Doing S2,1 Calibration..wait 4 seconds\n");
    sleep(4);
    button_command(":SENS1:CORR:COLL:SAVE\r\n");

    button_command(":INIT1:IMM\r\n");
    printf("\n\nCalibration Complete\n");
*/

/*  old scanf info to set up cal file
  printf("\nReconfigure for Phasing Card Measurements");
  mypause();
  ant=-1; 
  printf("\n\nEnter Radar Name: ");
  fflush(stdin);
  scanf("%s", &radar_name);
  fflush(stdout);
  fflush(stdin);
  printf("\n\nEnter ANTENNA Number: ");
  fflush(stdin);
  fflush(stdout);
  scanf("%d", &ant);
  printf("Radar: <%s>  Card: %d\n",radar_name,ant);
  fflush(stdout);
*/

/*  Old cal file setup
      count=ANTS;
      fwrite(&count,sizeof(int),1,calfile);
      count=CARDS;
      fwrite(&count,sizeof(int),1,calfile);
      count=fnum;
      fwrite(&count,sizeof(int),1,calfile);
      count=0;
      fwrite(freq,sizeof(double),fnum,calfile);
*/
    //button_command(":SENS1:AVER:CLE\r\n");
  while(1) {
    for(i=0;i<fnum;i++) {
      phase[i][0]=0;
      pwr_mag[i][0]=0;
    }
    printf("\nEnter Antenna Number: [%d] ",ant);
    fflush(stdin);
    fflush(stdout);
    fgets(input,20,stdin);
    if(strlen(input)>1) {
      new_ant=atoi(input);
      if(new_ant!=ant) iter=1;
      else iter++;
      ant=new_ant;
    } else {
      iter++;
    } 
    printf("\nEnter Iteration Number: [%d] ",iter);
    fflush(stdin);
    fflush(stdout);
    fgets(input,20,stdin);
    if(strlen(input)>1) {
      iter=atoi(input);
    } 
    printf("\nAnt: %d Iteration %d\n",ant,iter);
    sprintf(filename,"%s/%s_%03d_%03d%s",dir,file_prefix,ant,iter,file_ext);
    if (verbose>0) fprintf(stdout,"Using file: %s\n",filename);
    fflush(stdout);
    fp=fopen(filename,"w");

    button_command(":INIT1:IMM\r\n");
#ifdef __QNX__
      delay(10); //NO AVERAGE
#else
      usleep(5);
#endif
    printf("Freq 0: %lf Freq %d: %lf\n",freq[0],fnum-1,freq[fnum-1]);
    button_command(":CALC1:PAR1:SEL\r\n");
    mlog_data_command(":CALC1:DATA:FDAT?\r\n",phase,0) ;
    printf("Phase 0: %lf Phase %d: %lf\n",phase[0][0],fnum-1,phase[fnum-1][0]);
    button_command(":CALC1:PAR2:SEL\r\n");
    mlog_data_command(":CALC1:DATA:FDAT?\r\n",pwr_mag,0) ;
//    printf("Mag phase[fnum][0]-phase[0][0];
//  %lf Mag %d: %lf\n",pwr_mag[0][0],fnum-1,pwr_mag[fnum-1][0]);
/*
    length_avg=0.0;
    for(i=0;i<fnum;i++){
    	lambda=VELOCITY_FACTOR*3e8/freq[i];
	phi=-1*phase[i][0];
	length=phi*lambda/720.0;
	length_avg=length_avg+length;
    }
    length=length_avg/fnum;
*/
  float del_phi;
  float del_freq;
  del_phi = -1 *  3.14/180*( phase[fnum-1][0]-phase[0][0]);
  del_freq = 6.28*( fstop - fstart);
  float time_delay = del_phi/del_freq; 
  length = 0.5 *  3e8 * VELOCITY_FACTOR * time_delay;

    printf("The velocity factor is %lf\n", VELOCITY_FACTOR);
    printf("The target length is %lf meters (%lf feet)\n", TRIM_LENGTH_METERS,3.28*TRIM_LENGTH_METERS);
    printf("The length of the cable is %f meters (%f feet)\n", length, 3.28*length);
    printf("TRIM %f INCHES\n", 39.37*(length-TRIM_LENGTH_METERS));
    printf("SAFE TRIM %f INCHES\n", 0.5 *39.37*(length-TRIM_LENGTH_METERS));
    for(i=0;i<fnum;i++) {
      fprintf(fp,"%13d, %13.5lf,%13.5lf,%13.5lf\n",i,freq[i],phase[i][0],pwr_mag[i][0]);
    }
    fclose(fp);
  }
/* old cal file data write
    for(i=0;i<fnum;i++) {
      fwrite(&i,sizeof(int),1,calfile);
      count=fwrite(phase[i],sizeof(double),ANTS,calfile);
      count=fwrite(pwr_mag[i],sizeof(double),ANTS,calfile);
    }
    printf("Closing File\n");
    fclose(calfile);
*/
}

