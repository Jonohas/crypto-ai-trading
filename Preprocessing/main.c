#include<string.h>
#include<stdlib.h>

#include <stdio.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <stdbool.h>

#include <ta-lib/ta_libc.h>

#define MAX_LINE_LENGTH 80
#define CSV_LENGTH 525601

struct indicators {
    
};

struct candle {
    long time;
    double open;
    double close;
    double high;
    double low;
    double volume;

    double adosc;
    double atr;
    double bb_upper;
    double bb_middle;
    double bb_lower;
    double macd;
    double mfi;
    double rsi;
    double sar;
    double tema;
};

struct indicator_selection {
    // adsoc, atr, bb_upper, bb_middel, bb_lower, macd, mfi, rsi, sar, tema
    bool adosc;
    bool atr;
    bool bb;
    bool macd;
    bool mfi;
    bool rsi;
    bool sar;
    bool tema;
};

struct indicator_thread {
    char *input_file;
    char *output_file;
};

void calculate_indicators(struct indicator_selection *selection, struct candle *candles, char * output_file[]) {
    // adsoc, atr, bb_upper, bb_middel, bb_lower, macd, mfi, rsi, sar, tema
    
    double *temp_open = malloc(sizeof(double) * CSV_LENGTH);
    double *temp_high = malloc(sizeof(double) * CSV_LENGTH);
    double *temp_low = malloc(sizeof(double) * CSV_LENGTH);
    double *temp_close = malloc(sizeof(double) * CSV_LENGTH);
    double *temp_volume = malloc(sizeof(double) * CSV_LENGTH);

    for (int i = 0; i < CSV_LENGTH - 1 ; i++)
    {
        struct candle *candle = &candles[i];

        temp_open[i] = candle->open;
        temp_high[i] = candle->high;
        temp_low[i] = candle->low;
        temp_close[i] = candle->close;
        temp_volume[i] = candle->volume;
    }

    // free(candles);

    double *tmp_adosc = malloc(sizeof(double) * CSV_LENGTH);
    int beginIdx, endIdx;

    if (selection->adosc)
    {
        // TA_RetCode retCode = TA_ADOSC(0, CSV_LENGTH - 1, temp_high, temp_low, temp_close, temp_volume, 3, 10, &beginIdx, &endIdx, tmp_adosc);
        TA_ADOSC(0, CSV_LENGTH - 1, temp_high, temp_low, temp_close, temp_volume, 3, 10, &beginIdx, &endIdx, tmp_adosc);
    }


    // Assign the calculated values to the candles
    for (int i = 0; i < CSV_LENGTH; i++)
    {
        struct candle *candle = &candles[i];
        candle->adosc = tmp_adosc[i];
    }


    
    FILE *wfp = fopen(output_file, "a");
    for (int i = 0; i < CSV_LENGTH - 1 ; i++) {
        if (i ==0)
            fprintf(wfp, "%s,%s,%s,%s,%s,%s,%s\n", "event_time","open","close","high","low","volume","adosc");
        else {
            struct candle *candle = &candles[i];

            fprintf(wfp, "%ld,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf\n", 
                candle->time, 
                candle->open, 
                candle->close, 
                candle->high, 
                candle->low, 
                candle->volume, 
                candle->adosc
            );
        }
    }

    fclose(wfp);
    
    // free(tmp_adosc);
    // if (selection->atr)
    //     printf("atr");

    // if (selection->bb)
    //     printf("bb");

    // if (selection->macd)
    //     printf("macd");

    // if (selection->mfi)
    //     printf("mfi");

    // if (selection->rsi)
    //     printf("rsi");

    // if (selection->sar)
    //     printf("sar");

    // if (selection->tema)    
    //     printf("tema");
};

void *prepocess(void* args) {
    struct indicator_thread *thread_args = args;
    printf("%s\n", thread_args->input_file);

    char *filename_qfd = thread_args->input_file;

    char *output_file = thread_args->output_file;

    char str[MAX_LINE_LENGTH];
    int result;
    FILE *fp = fopen(filename_qfd, "r");

    struct candle *candles;


    // length of allocation is one year in minutes (minute candles)
    candles = calloc(CSV_LENGTH, sizeof(struct candle));
    // print size of struct candle
    if (candles == NULL) 
    {
        printf("Error allocating memory for candles\n");
        exit(1);
    }

    int count = 0;
    while (fgets(str, MAX_LINE_LENGTH, fp)) 
    {
        struct candle *c = (struct candle *)&candles[count - 1];
        sscanf(str, "%ld,%lf,%lf,%lf,%lf,%lf", &c->time, &c->open, &c->close, &c->high, &c->low, &c->volume);
        count++;
    }

    struct indicator_selection selection;

    selection.adosc = true;
    selection.atr = true;
    selection.bb = true;
    selection.macd = true;
    selection.mfi = true;
    selection.rsi = true;
    selection.sar = true;
    selection.tema = true;

    calculate_indicators(&selection, candles, output_file);

    fclose(fp);
    free(candles);
    printf("Finished file: %s\n", output_file);
}

int countfiles(char *path) {
    DIR *dir_ptr = NULL;
    struct dirent *direntp;
    char *npath;
    if (!path) return 0;
    if( (dir_ptr = opendir(path)) == NULL ) return 0;

    int count=0;
    while( (direntp = readdir(dir_ptr)))
    {
        if (strcmp(direntp->d_name,".")==0 ||
            strcmp(direntp->d_name,"..")==0) continue;
        switch (direntp->d_type) {
            case DT_REG:
                ++count;
                break;
            case DT_DIR:            
                npath=malloc(strlen(path)+strlen(direntp->d_name)+2);
                sprintf(npath,"%s/%s",path, direntp->d_name);
                count += countfiles(npath);
                free(npath);
                break;
        }
    }
    closedir(dir_ptr);
    return count;
}

int main(int argc, char** argv)   // define the main function  
{  
    char *input_folder = argv[1];
    char *output_folder = argv[2];
    struct dirent *dp;
    DIR *dfd;

    if ((dfd = opendir(input_folder)) == NULL)
    {
        fprintf(stderr, "Can't open %s\n", input_folder);
        return 0;
    }


    int num_files = countfiles(input_folder);
    char filename_qfd[300] ;
    char new_name_qfd[300] ;

    printf("Number of files: %d\n", num_files);
    pthread_t threads[num_files];

    int i = 0;
    while ((dp = readdir(dfd)) != NULL) {

        struct stat stbuf ;
        sprintf( filename_qfd , "%s%s",input_folder,dp->d_name) ;
        if( stat(filename_qfd,&stbuf ) == -1 )
        {
            printf("Unable to stat file: %s\n", filename_qfd) ;
            continue ;
        }
        if ( ( stbuf.st_mode & S_IFMT ) != S_IFDIR )
        {
            char *s = calloc(strlen(filename_qfd) + 1, sizeof(char));
            strcpy(s, filename_qfd);

            char *st = calloc(strlen(s) + 1, sizeof(char));
            strcpy(st, s);
            // printf("File: %s\n", s);

            char *filename_qfd = calloc(300, sizeof(char));
            char *new_name_qfd = calloc(300, sizeof(char));

            free(filename_qfd);
            free(new_name_qfd);

            char *token = strtok(s, "/");
            char file_name[10];

            while (token != NULL) {
                strcpy(file_name, token);
                token = strtok(NULL, "/");
            }

            char *output_file = calloc(300, sizeof(char));
            strcat(output_file, output_folder);
            strcat(output_file, file_name);

            struct indicator_thread *thread = malloc(sizeof(struct indicator_thread));
            thread->input_file = st;
            thread->output_file = output_file;

            free(s);
            pthread_create(&threads[i], NULL, prepocess, (void *)thread);
            i++;
        }
    }

    

    for (int j = 0; j < num_files; j++) {
        pthread_join(threads[j], NULL);
    }

    closedir(dfd);

    return 0;

}  