use std::io::prelude::*;
use flate2::write::GzDecoder;
use flate2::{Status, DecompressError};

/// Reads a given number of bytes from file and returns a slice containing them.
fn stream_read(file: &mut std::fs::File) -> std::io::Result<Vec<u8>>
{
    let mut buffer = [0u8; 8192];
    println!("Buffer size is {}", buffer.len());
    match file.read(&mut buffer) {
        Ok(bytes) => Ok(buffer[0..bytes].to_vec()),
        Err(msg) => Err(msg),
    }
}

struct Reader {
    source: std::fs::File,
}

struct Writer {
    destination: std::fs::File,
}

impl Read for Reader {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        let mut buffer = [0u8; 64];
        println!("Buffer size is {}", buffer.len());
        match self.source.read(&mut buffer) {
            Ok(bytes) => {
                buf[0..bytes].clone_from_slice(&buffer[0..bytes]);
                Ok(bytes)
            },
            Err(msg) => Err(msg),
        }
    }
}

impl Write for Writer {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        println!("Writing {} bytes into output file.", buf.len());
        self.destination.write(buf)
    }

    fn flush(&mut self) -> std::io::Result<()> {
        println!("Flusing.");
        Ok(())
    }
}

fn open_data_source() -> std::io::Result<std::fs::File> {
    std::fs::OpenOptions::new().read(true).open("./data/source.gz")
}

fn decompress(mut file: std::fs::File, output: std::fs::File) -> Vec<u8> {
    let mut total = 0;
    let mut content = Vec::<u8>::with_capacity(81920);
    let mut raw_reader = Reader { source: file };
    let mut raw_writer = Writer {  destination: output };
    let mut gz_decoder = flate2::write::GzDecoder::new(content);
    let mut gz_writer_decoder = flate2::write::GzDecoder::new(raw_writer);
    let mut buffer = [0u8; 8192];
    let mut decomp = flate2::Decompress::new(false);
    loop {
        match raw_reader.read(&mut buffer) {
            Ok(0) => {
                println!("Looks like the whole file has been read.");
                break
            },
            Ok(bytes) => {
                println!("Read {} bytes from file", bytes);
                gz_writer_decoder.write_all(&buffer[0..bytes]);
                gz_writer_decoder.flush();
                gz_decoder.write_all(&buffer[0..bytes]);
            },
            Err(msg) => println!("Failed to read from file: {}.", msg),
        }
    }

    gz_writer_decoder.flush();

    gz_writer_decoder.finish().unwrap();

    gz_decoder.finish().unwrap()
}

fn main() {
    println!("Starting.");

    match open_data_source() {
        Ok(mut input) => {
            let mut output = std::fs::OpenOptions::new().write(true).create(true).open("data/writer_decompressed.txt").unwrap();
            let content = decompress(input, output);
            let mut decompressed = std::fs::OpenOptions::new().write(true).create(true).open("data/reader_decompressed.txt").unwrap();
            decompressed.write(&content);
        },
        Err(msg) => println!("Failed to open file: {}.", msg),
    }
}
