use std::io::prelude::*;
use flate2::read::GzDecoder;

/// Reads a given number of bytes from file and returns a slice containing them.
fn stream_read(file: &mut std::fs::File) -> std::io::Result<Vec<u8>>
{
    let mut buffer = [0u8; 5];
    println!("Buffer size is {}", buffer.len());
    match file.read(&mut buffer) {
        Ok(bytes) => Ok(buffer[0..bytes].to_vec()),
        Err(msg) => Err(msg),
    }
}

struct Reader {
    source: std::fs::File,
}

impl Read for Reader {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        let mut buffer = [0u8; 5];
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

fn open_data_source() -> std::io::Result<std::fs::File> {
    std::fs::OpenOptions::new().read(true).open("./data/source.gz")
}

fn decompress(file: std::fs::File) -> String {
    let mut total = 0;
    let mut content = Vec::<u8>::new();
    let mut raw_reader = Reader { source: file };
    let mut gz_decoder = GzDecoder::new(raw_reader);
    let mut buffer = [0u8; 8192];
    loop {
        match  gz_decoder.read(&mut buffer) {
            Ok(0) => {
                println!("Looks like the whole file has been read.");
                break
            },
            Ok(bytes) => {
                content.extend(buffer);
                println!("Read {} bytes from file. Total: {}", buffer.len(), content.len())
            },
            Err(msg) => println!("Failed to read from file: {}.", msg),
        }
    }

    String::from_utf8(content).unwrap()
}

fn main() {
    println!("Starting.");

    match open_data_source() {
        Ok(mut file) => {
            let content = decompress(file);
            println!("Content decompressed is:\n\n=======\n{}\n=======\n", content)
        },
        Err(msg) => println!("Failed to open file: {}.", msg),
    }
}
