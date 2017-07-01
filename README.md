# starcraft-replay-highlighter
Project that analyses replay files for the game Starcraft and highlights important moments 

## Installation

Clone the github repository into a directory on your computer, than install the python requirements with:

```shell
pip install -r requirements.txt
```

Code needs python2.7 to run

You will also need the code from this commit: [csv generation](https://github.com/JAdeLeeuw/ScExtractor/tree/61b95dcc6962b708d9b3552ad1a24889f9b71496). This code will generate csv files from the starcraft replay file which can than be cosumed by this script. In the future we want to convert this to an all in one python script.

## Usage

Run the analyser.py file with a the only argument the location of a directory containing the generated csv intermediate stage files relative to the root repo directory. The output of the highlighting will be returned on the stdout. Several graphs will be generated and placed in the same diretory as the csv files. The path will also be in the output of the script.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning.

## Authors

See also the list of [contributors](https://github.com/mitchellolsthoorn/starcraft-replay-highlighter/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

