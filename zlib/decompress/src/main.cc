#include "zlib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static alloc_func zalloc = (alloc_func)0;
static free_func zfree = (free_func)0;
static z_const char hello[] = "hello, hello!";

#define CHECK_ERR(err, msg) { \
    if (err != Z_OK) { \
        fprintf(stderr, "%s error: %d\n", msg, err); \
        exit(1); \
    } \
}

uLong read_file(const char* filename, uLong buffer_size, void* buffer) {
    FILE* f = fopen(filename, "r");
    size_t read = fread(buffer, 1, buffer_size, f);
    fclose(f);

    return read;
}

void test_deflate(Byte* compr, uLong comprLen)
{
    z_stream c_stream; /* compression stream */
    int err;
    uLong len = (uLong)strlen(hello)+1;
    char output[1024];
    memset(output, 0, sizeof(output));

    c_stream.zalloc = zalloc;
    c_stream.zfree = zfree;
    c_stream.opaque = (voidpf)0;

    err = deflateInit(&c_stream, Z_DEFAULT_COMPRESSION);
    CHECK_ERR(err, "deflateInit");

    c_stream.next_in  = (z_const unsigned char *)hello;
    c_stream.next_out = compr;

    while (c_stream.total_in != len && c_stream.total_out < comprLen) {
        c_stream.avail_in = c_stream.avail_out = 1; /* force small buffers */
        err = deflate(&c_stream, Z_NO_FLUSH);
        CHECK_ERR(err, "deflate");
    }
    /* Finish the stream, still forcing small buffers: */
    for (;;) {
        c_stream.avail_out = 1;
        err = deflate(&c_stream, Z_FINISH);
        if (err == Z_STREAM_END) break;
        CHECK_ERR(err, "deflate");
    }

    err = deflateEnd(&c_stream);
    CHECK_ERR(err, "deflateEnd");

    printf("In: %lu Out: %lu\n", c_stream.total_in, c_stream.total_out);
}

void test_inflate(Byte* compr, uLong comprLen, Byte* uncompr, uLong uncomprLen)
{
    int err;
    z_stream d_stream; /* decompression stream */

    strcpy((char*)uncompr, "garbage");

    d_stream.zalloc = zalloc;
    d_stream.zfree = zfree;
    d_stream.opaque = (voidpf)0;

    d_stream.next_in  = compr;
    d_stream.avail_in = 0;
    d_stream.next_out = uncompr;

    err = inflateInit2(&d_stream, 16+MAX_WBITS);
    CHECK_ERR(err, "inflateInit");

    int counter = 0;

    while (d_stream.total_out < uncomprLen && d_stream.total_in < comprLen) {
        counter++;
        d_stream.avail_in = d_stream.avail_out = 1; /* force small buffers */
        err = inflate(&d_stream, Z_NO_FLUSH);
        if (err == Z_STREAM_END) break;
        CHECK_ERR(err, "inflate");
    }

    printf("Looped %d times. In: %lu Out: %lu", counter, d_stream.total_in, d_stream.total_out);

    err = inflateEnd(&d_stream);
    CHECK_ERR(err, "inflateEnd");

    printf("inflate(): %s\n", (char *)uncompr);
    printf("%lu length", strlen((char*)uncompr));
}

void test() {
    size_t size = 1024 * 1024 * 10;
    Byte* buffer = (Byte*)malloc(size);
    uLong available = read_file("test.gz", size, buffer);

    Byte *compr, *uncompr;
    uLong comprLen = 10000*sizeof(int); /* don't overflow on MSDOS */
    uLong uncomprLen = comprLen;

    compr    = (Byte*)calloc((uInt)comprLen, 1);
    uncompr  = (Byte*)calloc((uInt)uncomprLen, 1);

    //test_deflate(compr, comprLen);
    comprLen = available;
    compr = buffer;

    test_inflate(compr, comprLen, uncompr, uncomprLen);
}


int main(int argc, char* argv[]) {
    test();
    return 0;
}
