use clap::{Parser, Subcommand};

/// Ace-Em command-line interface.
#[derive(Parser, Debug)]
#[command(
    name = "ace-em",
    version,
    about = "Command-line entrypoint for Ace-Em",
    long_about = "A lightweight CLI scaffold ready for future Ace-Em features."
)]
struct Cli {
    /// Subcommand to run
    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand, Debug)]
enum Command {
    /// Print a friendly greeting
    Greet {
        /// Name to greet
        #[arg(short, long, default_value = "friend")]
        name: String,
    },
    /// Show basic information about the CLI
    Info,
}

fn main() {
    let cli = Cli::parse();

    match cli.command.unwrap_or(Command::Info) {
        Command::Greet { name } => println!("Hello, {name}! Welcome to Ace-Em."),
        Command::Info => print_info(),
    }
}

fn print_info() {
    println!("Ace-Em CLI is ready. Try `ace-em greet --name <you>` to say hello.");
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::CommandFactory;

    #[test]
    fn cli_debug_asserts() {
        Cli::command().debug_assert();
    }
}
